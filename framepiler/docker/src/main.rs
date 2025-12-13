// Frame Docker Test Runner - Pure Rust implementation
// Replaces the Python docker_test_harness.py

use anyhow::{anyhow, Context, Result};
use clap::Parser;
use colored::*;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::Instant;
use walkdir::WalkDir;

#[derive(Parser, Debug)]
#[command(name = "frame-docker-runner")]
#[command(about = "Run Frame tests in Docker containers", long_about = None)]
struct Args {
    /// Target language (python_3, typescript, rust)
    language: String,

    /// Test category (e.g., v3_data_types) or specific .frm file
    category: String,

    /// Path to framec binary
    #[arg(long, default_value = "./target/release/framec")]
    framec: PathBuf,

    /// Path to shared test environment
    #[arg(long)]
    shared_env: Option<PathBuf>,

    /// Output results as JSON
    #[arg(long)]
    json: bool,

    /// Verbose output
    #[arg(short, long)]
    verbose: bool,
}

/// Test execution result
#[derive(Debug, Clone, Serialize, Deserialize)]
struct TestResult {
    test: String,
    language: String,
    transpiled: bool,
    executed: bool,
    passed: bool,
    output: String,
    error: Option<String>,
    duration_ms: u128,
}

/// Test runner implementation
struct DockerTestRunner {
    framec_path: PathBuf,
    shared_env: PathBuf,
    verbose: bool,
}

impl DockerTestRunner {
    fn new(framec_path: PathBuf, shared_env: PathBuf, verbose: bool) -> Result<Self> {
        // Verify framec exists
        if !framec_path.exists() {
            return Err(anyhow!("framec binary not found: {}", framec_path.display()));
        }

        // Verify shared environment exists
        if !shared_env.exists() {
            return Err(anyhow!("Shared environment not found: {}", shared_env.display()));
        }

        Ok(Self {
            framec_path,
            shared_env,
            verbose,
        })
    }

    /// Check if a test file is for the target language
    fn is_test_for_language(&self, test_file: &Path, language: &str) -> bool {
        let content = match fs::read_to_string(test_file) {
            Ok(c) => c,
            Err(_) => return false,
        };

        // Look for @target annotation in first 5 lines
        for line in content.lines().take(5) {
            let line = line.trim();
            if line.starts_with("@target") {
                let target = line.split_whitespace().nth(1).unwrap_or("");
                let lang_matches = match language {
                    "python_3" | "python" => {
                        target == "python" || target == "py" || target == "python_3"
                    }
                    "typescript" => target == "typescript" || target == "ts",
                    "rust" => target == "rust" || target == "rs",
                    _ => false,
                };
                return lang_matches;
            }
        }

        // No @target means it's for all languages
        true
    }

    /// Find test files in a category
    fn find_test_files(&self, category: &str, language: &str) -> Result<Vec<PathBuf>> {
        // Handle single file
        if category.ends_with(".frm") || category.ends_with(".frm_v3") {
            let test_file = self.shared_env
                .join("common/test-frames/v3")
                .join(category);
            if test_file.exists() {
                return Ok(vec![test_file]);
            }
            return Err(anyhow!("Test file not found: {}", category));
        }

        // Find test directory
        let category_name = category.strip_prefix("v3_").unwrap_or(category);
        let test_dir = self.shared_env
            .join("common/test-frames/v3")
            .join(category_name)
            .join("positive");

        if !test_dir.exists() {
            return Err(anyhow!("Test directory not found: {}", test_dir.display()));
        }

        // Find all .frm and .frm_v3 files
        let mut test_files = Vec::new();
        for entry in WalkDir::new(&test_dir).max_depth(1) {
            let entry = entry?;
            let path = entry.path();
            let ext = path.extension().and_then(|s| s.to_str());
            
            // Check for both .frm and .frm_v3 extensions
            let is_frame_file = ext == Some("frm") || 
                                path.to_string_lossy().ends_with(".frm_v3");
            
            if is_frame_file {
                if self.is_test_for_language(path, language) {
                    test_files.push(path.to_path_buf());
                } else if self.verbose {
                    println!("{} {} (not for {})", 
                        "Skipping".yellow(),
                        path.file_name().unwrap().to_string_lossy(),
                        language
                    );
                }
            }
        }

        test_files.sort();
        Ok(test_files)
    }

    /// Transpile a test file
    fn transpile(&self, test_file: &Path, language: &str, output_dir: &Path) -> Result<PathBuf> {
        let ext = match language {
            "python_3" | "python" => "py",
            "typescript" => "ts",
            "rust" => "rs",
            _ => return Err(anyhow!("Unsupported language: {}", language)),
        };

        // Handle .frm_v3 files by stripping the full extension
        let file_name = test_file.file_name().unwrap().to_string_lossy();
        let base_name = if file_name.ends_with(".frm_v3") {
            file_name.strip_suffix(".frm_v3").unwrap().to_string()
        } else if file_name.ends_with(".frm") {
            file_name.strip_suffix(".frm").unwrap().to_string()
        } else {
            test_file.file_stem().unwrap().to_string_lossy().to_string()
        };

        let output_file = output_dir.join(format!("{}.{}", base_name, ext));

        // Run framec
        let output = Command::new(&self.framec_path)
            .args(&["-l", language])
            .arg(test_file)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .output()
            .context("Failed to run framec")?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow!("Transpilation failed: {}", stderr));
        }

        // Write output
        fs::write(&output_file, &output.stdout)?;
        Ok(output_file)
    }

    /// Compile TypeScript to JavaScript using esbuild
    fn compile_typescript(&self, ts_file: &Path) -> Result<PathBuf> {
        let js_file = ts_file.with_extension("js");

        let output = Command::new("npx")
            .arg("esbuild")
            .arg(ts_file)
            .arg("--bundle")
            .arg("--platform=node")
            .arg("--target=node14")
            .arg("--format=cjs")
            .arg("--external:frame_runtime_ts")
            .arg(format!("--outfile={}", js_file.display()))
            .current_dir(ts_file.parent().unwrap())
            .output()
            .context("Failed to run esbuild")?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow!("TypeScript compilation failed: {}", stderr));
        }

        Ok(js_file)
    }

    /// Run test in Docker
    fn run_in_docker(&self, language: &str, test_file: &Path) -> Result<(bool, String)> {
        let image = match language {
            "python_3" | "python" => "frame-transpiler-python:latest",
            "typescript" => "frame-transpiler-typescript:latest",
            "rust" => "frame-transpiler-rust:latest",
            _ => return Err(anyhow!("Unsupported language: {}", language)),
        };

        let test_dir = test_file.parent().unwrap();
        let test_name = test_file.file_name().unwrap().to_string_lossy();

        let mut cmd = Command::new("docker");
        cmd.arg("run").arg("--rm")
            .arg("-v").arg(format!("{}:/work", test_dir.display()));

        // Add runtime mounts
        match language {
            "python_3" | "python" => {
                let runtime = self.shared_env.join("framepiler/frame_runtime_py");
                cmd.arg("-v").arg(format!("{}:/opt/frame_runtime_py", runtime.display()))
                    .arg("-e").arg("PYTHONPATH=/opt:/work");
            }
            "typescript" => {
                let runtime = self.shared_env.join("framepiler/frame_runtime_ts");
                cmd.arg("-v").arg(format!("{}:/opt/frame_runtime_ts", runtime.display()))
                    .arg("-e").arg("NODE_PATH=/opt");
            }
            _ => {}
        }

        // Add image and command
        cmd.arg(image);

        match language {
            "python_3" | "python" => {
                cmd.arg("python3").arg(format!("/work/{}", test_name));
            }
            "typescript" => {
                cmd.arg("node").arg(format!("/work/{}", test_name));
            }
            "rust" => {
                cmd.arg("bash").arg("-c")
                    .arg(format!(
                        "cd /work && rustc {} -o test_binary 2>&1 && ./test_binary 2>&1",
                        test_name
                    ));
            }
            _ => {}
        }

        let output = cmd.output().context("Failed to run Docker")?;
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        let combined = format!("{}{}", stdout, stderr);

        Ok((output.status.success(), combined))
    }

    /// Run a single test
    fn run_test(&self, test_file: &Path, language: &str) -> TestResult {
        let start = Instant::now();
        let test_name = test_file.to_string_lossy().to_string();

        // Create temp directory
        let temp_dir = match tempfile::tempdir() {
            Ok(d) => d,
            Err(e) => {
                return TestResult {
                    test: test_name,
                    language: language.to_string(),
                    transpiled: false,
                    executed: false,
                    passed: false,
                    output: String::new(),
                    error: Some(format!("Failed to create temp dir: {}", e)),
                    duration_ms: start.elapsed().as_millis(),
                };
            }
        };

        // Transpile
        let transpiled_file = match self.transpile(test_file, language, temp_dir.path()) {
            Ok(f) => f,
            Err(e) => {
                return TestResult {
                    test: test_name,
                    language: language.to_string(),
                    transpiled: false,
                    executed: false,
                    passed: false,
                    output: String::new(),
                    error: Some(format!("Transpilation failed: {}", e)),
                    duration_ms: start.elapsed().as_millis(),
                };
            }
        };

        // Compile TypeScript if needed
        let exec_file = if language == "typescript" {
            match self.compile_typescript(&transpiled_file) {
                Ok(f) => f,
                Err(e) => {
                    return TestResult {
                        test: test_name,
                        language: language.to_string(),
                        transpiled: true,
                        executed: false,
                        passed: false,
                        output: String::new(),
                        error: Some(format!("TypeScript compilation failed: {}", e)),
                        duration_ms: start.elapsed().as_millis(),
                    };
                }
            }
        } else {
            transpiled_file
        };

        // Execute in Docker
        let (success, output) = match self.run_in_docker(language, &exec_file) {
            Ok((s, o)) => (s, o),
            Err(e) => {
                return TestResult {
                    test: test_name,
                    language: language.to_string(),
                    transpiled: true,
                    executed: false,
                    passed: false,
                    output: String::new(),
                    error: Some(format!("Docker execution failed: {}", e)),
                    duration_ms: start.elapsed().as_millis(),
                };
            }
        };

        TestResult {
            test: test_name,
            language: language.to_string(),
            transpiled: true,
            executed: true,
            passed: success,
            output,
            error: if success { None } else { Some("Test failed".to_string()) },
            duration_ms: start.elapsed().as_millis(),
        }
    }

    /// Run all tests in a category
    fn run_category(&self, language: &str, category: &str) -> Result<Vec<TestResult>> {
        let test_files = self.find_test_files(category, language)?;
        
        if test_files.is_empty() {
            return Err(anyhow!("No test files found for {} in {}", language, category));
        }

        println!("Running {} tests for {}/{}", 
            test_files.len(), language, category);
        println!("{}", "=".repeat(60));

        let mut results = Vec::new();
        for test_file in test_files {
            let test_name = test_file.file_name().unwrap().to_string_lossy();
            print!("Running {}... ", test_name);
            
            let result = self.run_test(&test_file, language);
            
            if result.passed {
                println!("{}", "✓ PASSED".green());
            } else {
                println!("{} - {}", 
                    "✗ FAILED".red(),
                    result.error.as_ref().unwrap_or(&"Unknown error".to_string())
                );
            }
            
            if self.verbose && !result.output.is_empty() {
                println!("  Output: {}", result.output.trim());
            }
            
            results.push(result);
        }

        Ok(results)
    }
}

fn main() -> Result<()> {
    let args = Args::parse();

    // Find shared environment
    let shared_env = if let Some(env_path) = args.shared_env {
        env_path
    } else if let Ok(env_path) = std::env::var("FRAMEPILER_TEST_ENV") {
        PathBuf::from(env_path)
    } else {
        // Try to find relative to current directory
        let possible_path = PathBuf::from("framepiler_test_env");
        if possible_path.exists() {
            possible_path.canonicalize()?
        } else {
            return Err(anyhow!(
                "Could not locate shared test environment. Set FRAMEPILER_TEST_ENV or use --shared-env"
            ));
        }
    };

    // Create runner
    let runner = DockerTestRunner::new(args.framec, shared_env, args.verbose)?;

    // Run tests
    let results = runner.run_category(&args.language, &args.category)?;

    // Count results
    let passed = results.iter().filter(|r| r.passed).count();
    let failed = results.len() - passed;

    // Output results
    if args.json {
        let summary = serde_json::json!({
            "language": args.language,
            "category": args.category,
            "passed": passed,
            "failed": failed,
            "tests": results,
        });
        println!("{}", serde_json::to_string_pretty(&summary)?);
    } else {
        println!("{}", "=".repeat(60));
        println!("Summary for {}/{}:", args.language, args.category);
        println!("  {} Passed", format!("{}", passed).green());
        println!("  {} Failed", format!("{}", failed).red());
        println!("  Total: {}", results.len());
        println!("{}", "=".repeat(60));
    }

    // Exit with error if any tests failed
    std::process::exit(if failed == 0 { 0 } else { 1 })
}