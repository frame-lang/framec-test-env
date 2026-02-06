// Frame Docker Test Runner - Pure Rust implementation
// Replaces the Python docker_test_harness.py

use anyhow::{anyhow, Context, Result};
use chrono;
use clap::Parser;
use colored::*;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::time::Instant;
use walkdir::WalkDir;

#[derive(Parser, Debug)]
#[command(name = "frame-docker-runner")]
#[command(about = "Run Frame tests in Docker containers - by default runs ALL tests for ALL languages", long_about = None)]
struct Args {
    /// Path to framec binary
    #[arg(long, default_value = "./target/release/framec")]
    framec: PathBuf,

    /// Path to shared test environment
    #[arg(long)]
    shared_env: Option<PathBuf>,

    /// Filter by specific languages (comma-separated: python_3,typescript,rust)
    #[arg(long, value_delimiter = ',')]
    languages: Option<Vec<String>>,

    /// Filter by specific categories (comma-separated: data_types,async,core)
    #[arg(long, value_delimiter = ',')]
    categories: Option<Vec<String>>,

    /// Run specific .frm file
    #[arg(long)]
    file: Option<String>,

    /// Output results as JSON
    #[arg(long)]
    json: bool,

    /// Verbose output
    #[arg(short, long)]
    verbose: bool,

    /// Run comprehensive test summary across all categories
    #[arg(long)]
    summary: bool,

    /// Number of tests to run in parallel (default: 8)
    #[arg(long, default_value = "8")]
    parallel: usize,
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

    /// Check if a test file should be included based on language filters
    fn should_include_test(&self, test_file: &Path, language_filters: Option<&Vec<String>>) -> bool {
        let content = match fs::read_to_string(test_file) {
            Ok(c) => c,
            Err(_) => return false,
        };

        // Get the target language from the file
        let target_language = self.get_target_language_from_content(&content);

        // Exclude files without @@target
        if target_language.is_empty() {
            return false;
        }

        // If no language filters, include all tests
        let Some(filters) = language_filters else {
            return !self.should_skip_test(&content, &target_language);
        };

        // Check if target language matches any filter
        let matches_filter = filters.iter().any(|filter| {
            match filter.as_str() {
                "python_3" | "python" => {
                    target_language == "python_3" || target_language == "python"
                }
                "typescript" | "ts" => target_language == "typescript",
                "rust" | "rs" => target_language == "rust",
                "c" => target_language == "c",
                "cpp" | "c++" => target_language == "cpp",
                "java" => target_language == "java",
                "csharp" | "c#" => target_language == "csharp",
                "go" => target_language == "go",
                _ => &target_language == filter, // Direct match for other languages
            }
        });

        matches_filter && !self.should_skip_test(&content, &target_language)
    }

    /// Get target language from file content
    /// Returns empty string if no @@target found (file will be skipped)
    fn get_target_language_from_content(&self, content: &str) -> String {
        // Look for @@target annotation in first 5 lines
        for line in content.lines().take(5) {
            let line = line.trim();
            if line.starts_with("@@target") {
                let target = line.split_whitespace().nth(1).unwrap_or("");
                match target {
                    "python" | "py" | "python_3" => return "python_3".to_string(),
                    "typescript" | "ts" => return "typescript".to_string(),
                    "rust" | "rs" => return "rust".to_string(),
                    "c" => return "c".to_string(),
                    "cpp" | "c++" => return "cpp".to_string(),
                    "java" => return "java".to_string(),
                    "csharp" | "c#" => return "csharp".to_string(),
                    "go" => return "go".to_string(),
                    _ => return target.to_string(),
                }
            }
        }
        // No @@target found - return empty string to indicate invalid file
        String::new()
    }

    /// Check if a test should be skipped due to special conditions
    fn should_skip_test(&self, content: &str, target_language: &str) -> bool {
        // Check for skip conditions
        for line in content.lines().take(10) {
            let line = line.trim();
            // Skip Rust async tests that require tokio in simple Docker environment
            if line.contains("@skip-if: tokio-unavailable") && target_language == "rust" {
                return true;
            }
        }
        false
    }

    /// Find all available test categories
    fn find_all_categories(&self) -> Result<Vec<String>> {
        let v3_dir = self.shared_env.join("common/test-frames/v3");
        if !v3_dir.exists() {
            return Err(anyhow!("V3 test directory not found: {}", v3_dir.display()));
        }

        let mut categories = Vec::new();
        for entry in fs::read_dir(&v3_dir)? {
            let entry = entry?;
            let path = entry.path();
            if path.is_dir() {
                if let Some(name) = path.file_name().and_then(|n| n.to_str()) {
                    // Skip special files and directories
                    if !name.starts_with('.') && name != "test_simple_docker.frm" {
                        categories.push(name.to_string());
                    }
                }
            }
        }
        categories.sort();
        Ok(categories)
    }

    /// Find test files based on filters
    fn find_test_files_filtered(
        &self, 
        category_filters: Option<&Vec<String>>,
        language_filters: Option<&Vec<String>>,
        specific_file: Option<&String>
    ) -> Result<Vec<(PathBuf, String)>> {
        // Handle specific file
        if let Some(file_name) = specific_file {
            let test_file = if file_name.contains('/') {
                PathBuf::from(file_name)
            } else {
                self.shared_env
                    .join("common/test-frames/v3")
                    .join(file_name)
            };
            
            if test_file.exists() {
                let target_lang = self.get_target_language(&test_file);
                return Ok(vec![(test_file, target_lang)]);
            }
            return Err(anyhow!("Test file not found: {}", file_name));
        }

        // Get categories to search
        let categories = if let Some(filters) = category_filters {
            filters.clone()
        } else {
            self.find_all_categories()?
        };

        let mut all_test_files = Vec::new();

        // Search each category
        for category in categories {
            let category_path = self.shared_env
                .join("common/test-frames/v3")
                .join(&category);

            // Try positive directory first, then category root
            let search_dirs = [
                category_path.join("positive"),
                category_path.clone(),
            ];

            for search_dir in &search_dirs {
                if search_dir.exists() {
                    let test_files = self.find_test_files_in_directory(search_dir, language_filters)?;
                    all_test_files.extend(test_files);
                    break; // Found tests in this directory, don't search the other
                }
            }
        }

        all_test_files.sort_by(|a, b| a.0.cmp(&b.0));
        Ok(all_test_files)
    }

    /// Find test files in a specific directory
    fn find_test_files_in_directory(
        &self,
        dir: &Path,
        language_filters: Option<&Vec<String>>
    ) -> Result<Vec<(PathBuf, String)>> {
        let mut test_files = Vec::new();

        for entry in WalkDir::new(dir).max_depth(3) {
            let entry = entry?;
            let path = entry.path();
            
            // Skip directories
            if path.is_dir() {
                continue;
            }

            let ext = path.extension().and_then(|s| s.to_str());
            
            // Check for V3 Frame extensions
            let is_frame_file = ext == Some("frm") || 
                                path.to_string_lossy().ends_with(".frm_v3") ||
                                ext == Some("fpy") ||  // Python
                                ext == Some("frts") || // TypeScript  
                                ext == Some("frs") ||  // Rust
                                ext == Some("fc") ||   // C
                                ext == Some("fcpp") || // C++
                                ext == Some("frcs") || // C#
                                ext == Some("fjava");  // Java
            
            if is_frame_file {
                if self.should_include_test(path, language_filters) {
                    let target_lang = self.get_target_language(path);
                    test_files.push((path.to_path_buf(), target_lang));
                } else if self.verbose {
                    let content = fs::read_to_string(path).unwrap_or_default();
                    let target_lang = self.get_target_language_from_content(&content);
                    println!("{} {} [{}] (filtered out)", 
                        "Skipping".yellow(),
                        path.file_name().unwrap().to_string_lossy(),
                        target_lang
                    );
                }
            }
        }

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

        // Handle V3 extensions: .frm, .frm_v3, and language-specific (.fpy, .frts, .frs, etc.)
        let file_name = test_file.file_name().unwrap().to_string_lossy();
        let base_name = if file_name.ends_with(".frm_v3") {
            file_name.strip_suffix(".frm_v3").unwrap().to_string()
        } else if file_name.ends_with(".frm") {
            file_name.strip_suffix(".frm").unwrap().to_string()
        } else if file_name.ends_with(".fpy") {
            file_name.strip_suffix(".fpy").unwrap().to_string()
        } else if file_name.ends_with(".frts") {
            file_name.strip_suffix(".frts").unwrap().to_string()
        } else if file_name.ends_with(".frs") {
            file_name.strip_suffix(".frs").unwrap().to_string()
        } else if file_name.ends_with(".fc") {
            file_name.strip_suffix(".fc").unwrap().to_string()
        } else if file_name.ends_with(".fcpp") {
            file_name.strip_suffix(".fcpp").unwrap().to_string()
        } else if file_name.ends_with(".frcs") {
            file_name.strip_suffix(".frcs").unwrap().to_string()
        } else if file_name.ends_with(".fjava") {
            file_name.strip_suffix(".fjava").unwrap().to_string()
        } else {
            test_file.file_stem().unwrap().to_string_lossy().to_string()
        };

        let output_file = output_dir.join(format!("{}.{}", base_name, ext));

        // Build command with environment variables
        let mut cmd = Command::new(&self.framec_path);
        cmd.args(&["compile"])
            .arg(test_file)
            .args(&["-l", language])
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());

        // For Rust tests, set FRAME_EMIT_EXEC=1 to generate main function
        if language == "rust" {
            cmd.env("FRAME_EMIT_EXEC", "1");
        }

        let output = cmd.output().context("Failed to run framec")?;

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
                        "cd /work && rustc --edition 2021 {} -o test_binary 2>&1 && ./test_binary 2>&1",
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

    /// Get the target language for a test file from its @@target pragma
    fn get_target_language(&self, test_file: &Path) -> String {
        let content = match fs::read_to_string(test_file) {
            Ok(c) => c,
            Err(_) => return String::new(), // Return empty on read error
        };

        // Use the common method
        self.get_target_language_from_content(&content)
    }

    /// Run filtered tests
    fn run_filtered_tests(
        &self,
        category_filters: Option<&Vec<String>>,
        language_filters: Option<&Vec<String>>,
        specific_file: Option<&String>,
        parallel_count: usize
    ) -> Result<Vec<TestResult>> {
        let test_files = self.find_test_files_filtered(category_filters, language_filters, specific_file)?;
        
        if test_files.is_empty() {
            return Err(anyhow!("No test files found matching the specified filters"));
        }

        // Create filter description
        let filter_desc = self.build_filter_description(category_filters, language_filters, specific_file);
        
        println!("Running {} tests {} (parallel: {})", test_files.len(), filter_desc, parallel_count);
        println!("{}", "=".repeat(80));

        // Use atomic counter for progress tracking
        let completed = Arc::new(AtomicUsize::new(0));
        let total = test_files.len();
        
        // Configure thread pool
        let results = rayon::ThreadPoolBuilder::new()
            .num_threads(parallel_count)
            .build()
            .context("Failed to build thread pool")?
            .install(|| {
                // Run tests in parallel
                let results: Vec<TestResult> = test_files
                    .into_par_iter()
                    .map(|(test_file, target_lang)| {
                        let test_name = test_file.file_name().unwrap().to_string_lossy();
                        
                        // Show category in path for context
                        let category = test_file.parent()
                            .and_then(|p| p.file_name())
                            .map(|n| n.to_string_lossy())
                            .unwrap_or("unknown".into());
                        
                        let result = self.run_test(&test_file, &target_lang);
                        
                        // Update progress counter
                        let count = completed.fetch_add(1, Ordering::SeqCst) + 1;
                        
                        // Thread-safe printing
                        let status_str = if result.passed {
                            format!("✓ PASSED")
                        } else {
                            format!("✗ FAILED - {}", 
                                result.error.as_ref().unwrap_or(&"Unknown error".to_string()))
                        };
                        
                        println!("[{}/{}] {}/{} [{}]... {}", 
                            count, total, category, test_name, target_lang,
                            if result.passed { 
                                status_str.green().to_string() 
                            } else { 
                                status_str.red().to_string() 
                            }
                        );
                        
                        if self.verbose && !result.output.is_empty() {
                            println!("  Output: {}", result.output.trim());
                        }
                        
                        result
                    })
                    .collect();
                
                results
            });
        
        Ok(results)
    }

    /// Build a description of current filters for display
    fn build_filter_description(
        &self,
        category_filters: Option<&Vec<String>>,
        language_filters: Option<&Vec<String>>,
        specific_file: Option<&String>
    ) -> String {
        if let Some(file) = specific_file {
            return format!("for file: {}", file);
        }

        let mut parts = Vec::new();

        if let Some(categories) = category_filters {
            parts.push(format!("categories: {}", categories.join(",")));
        } else {
            parts.push("all categories".to_string());
        }

        if let Some(languages) = language_filters {
            parts.push(format!("languages: {}", languages.join(",")));
        } else {
            parts.push("all languages".to_string());
        }

        format!("({})", parts.join(", "))
    }
}

/// Run comprehensive test summary across all categories  
fn run_comprehensive_summary(
    runner: &DockerTestRunner,
    category_filters: Option<&Vec<String>>,
    language_filters: Option<&Vec<String>>,
    parallel_count: usize
) -> Result<()> {
    println!("================================================================");
    println!("          FRAME TRANSPILER COMPREHENSIVE TEST REPORT");
    println!("================================================================");
    
    let filter_desc = runner.build_filter_description(category_filters, language_filters, None);
    println!("Filters: {}", filter_desc);
    println!("Parallel: {} threads", parallel_count);
    println!("Date: {}", chrono::Utc::now().format("%Y-%m-%d %H:%M:%S UTC"));
    println!("");

    // Get all available categories
    let all_categories = runner.find_all_categories()?;
    
    // Filter categories if specified
    let categories_to_test = if let Some(filters) = category_filters {
        filters.iter().filter(|c| all_categories.contains(c)).cloned().collect()
    } else {
        all_categories
    };

    let mut total_passed = 0;
    let mut total_failed = 0;
    let mut total_tests = 0;
    let mut categories_with_tests = 0;

    for category in &categories_to_test {
        print!("  {:20}: ", category);
        std::io::stdout().flush().unwrap();

        // Run tests for this specific category
        let category_filter = vec![category.clone()];
        match runner.run_filtered_tests(Some(&category_filter), language_filters, None, parallel_count) {
            Ok(results) => {
                if results.is_empty() {
                    println!("no tests");
                } else {
                    let passed = results.iter().filter(|r| r.passed).count();
                    let failed = results.len() - passed;
                    let total = results.len();
                    
                    if failed == 0 {
                        println!("✅ {} tests ({} passed)", total, passed);
                    } else {
                        println!("⚠️  {} tests ({} passed, {} failed)", total, passed, failed);
                    }
                    
                    total_passed += passed;
                    total_failed += failed; 
                    total_tests += total;
                    categories_with_tests += 1;
                }
            }
            Err(e) => {
                if e.to_string().contains("No test files found") {
                    println!("no tests");
                } else {
                    println!("❌ ERROR: {}", e);
                }
            }
        }
    }

    println!("");
    println!("================================================================");
    println!("SUMMARY");
    println!("================================================================");
    println!("Categories with tests: {}", categories_with_tests);
    println!("Total tests executed: {}", total_tests);
    
    if total_tests > 0 {
        let success_rate = (total_passed as f64 / total_tests as f64) * 100.0;
        println!("Tests passed: {} ({:.1}%)", total_passed, success_rate);
        println!("Tests failed: {}", total_failed);
        
        if total_failed == 0 {
            println!("🎉 ALL TESTS PASSED!");
        } else {
            println!("⚠️  {} test(s) need attention", total_failed);
        }
    } else {
        println!("No tests found matching the specified filters");
    }
    
    println!("================================================================");

    // Exit with failure if any tests failed
    std::process::exit(if total_failed == 0 { 0 } else { 1 })
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

    // Handle summary mode
    if args.summary {
        return run_comprehensive_summary(&runner, args.categories.as_ref(), args.languages.as_ref(), args.parallel);
    }

    // Run tests with filters
    let results = runner.run_filtered_tests(
        args.categories.as_ref(),
        args.languages.as_ref(), 
        args.file.as_ref(),
        args.parallel
    )?;

    // Count results
    let passed = results.iter().filter(|r| r.passed).count();
    let failed = results.len() - passed;

    // Output results
    if args.json {
        let summary = serde_json::json!({
            "filters": {
                "languages": args.languages,
                "categories": args.categories,
                "file": args.file
            },
            "passed": passed,
            "failed": failed,
            "tests": results,
        });
        println!("{}", serde_json::to_string_pretty(&summary)?);
    } else {
        let filter_desc = runner.build_filter_description(
            args.categories.as_ref(),
            args.languages.as_ref(),
            args.file.as_ref()
        );
        println!("{}", "=".repeat(80));
        println!("Summary {}:", filter_desc);
        println!("  {} Passed", format!("{}", passed).green());
        println!("  {} Failed", format!("{}", failed).red());
        println!("  Total: {}", results.len());
        println!("{}", "=".repeat(80));
    }

    // Exit with error if any tests failed
    std::process::exit(if failed == 0 { 0 } else { 1 })
}