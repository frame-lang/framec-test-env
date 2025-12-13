// Docker executor for Frame test harness
// This module runs transpiled tests in Docker containers

use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::Duration;
use anyhow::{anyhow, Context, Result};
use serde::{Deserialize, Serialize};

/// Docker configuration for test execution
#[derive(Debug, Clone)]
pub struct DockerConfig {
    pub image_prefix: String,
    pub registry: Option<String>,
    pub timeout: Duration,
    pub mount_runtime: bool,
}

impl Default for DockerConfig {
    fn default() -> Self {
        Self {
            image_prefix: "frame-transpiler".to_string(),
            registry: None,
            timeout: Duration::from_secs(60),
            mount_runtime: true,
        }
    }
}

/// Docker executor for running tests in containers
pub struct DockerExecutor {
    config: DockerConfig,
    shared_env_path: PathBuf,
}

impl DockerExecutor {
    /// Create a new Docker executor
    pub fn new(shared_env_path: PathBuf, config: DockerConfig) -> Self {
        Self {
            config,
            shared_env_path,
        }
    }

    /// Get the Docker image name for a language
    fn get_image_name(&self, language: &str) -> String {
        let lang_name = match language {
            "python_3" | "python" => "python",
            "typescript" => "typescript",
            "rust" => "rust",
            _ => language,
        };

        if let Some(registry) = &self.config.registry {
            format!("{}/{}-{}:latest", registry, self.config.image_prefix, lang_name)
        } else {
            format!("{}-{}:latest", self.config.image_prefix, lang_name)
        }
    }

    /// Run a transpiled test in Docker
    pub fn run_test(
        &self,
        language: &str,
        test_file: &Path,
        additional_args: Vec<String>,
    ) -> Result<TestResult> {
        let image = self.get_image_name(language);
        let test_dir = test_file.parent()
            .ok_or_else(|| anyhow!("Test file has no parent directory"))?;
        let test_name = test_file.file_name()
            .ok_or_else(|| anyhow!("Test file has no name"))?
            .to_string_lossy();

        // Build Docker command
        let mut cmd = Command::new("docker");
        cmd.arg("run")
            .arg("--rm")
            .arg("-v")
            .arg(format!("{}:/work", test_dir.display()));

        // Add runtime mounts if needed
        if self.config.mount_runtime {
            match language {
                "python_3" | "python" => {
                    let runtime_path = self.shared_env_path.join("framepiler/frame_runtime_py");
                    cmd.arg("-v")
                        .arg(format!("{}:/opt/frame_runtime_py", runtime_path.display()))
                        .arg("-e")
                        .arg("PYTHONPATH=/opt:/work");
                }
                "typescript" => {
                    let runtime_path = self.shared_env_path.join("framepiler/frame_runtime_ts");
                    cmd.arg("-v")
                        .arg(format!("{}:/opt/frame_runtime_ts", runtime_path.display()))
                        .arg("-e")
                        .arg("NODE_PATH=/opt");
                }
                _ => {}
            }
        }

        // Add image and command
        cmd.arg(&image);

        // Language-specific execution
        match language {
            "python_3" | "python" => {
                cmd.arg("python3")
                    .arg(format!("/work/{}", test_name));
            }
            "typescript" => {
                // Assumes TypeScript is already compiled to JavaScript
                cmd.arg("node")
                    .arg(format!("/work/{}", test_name));
            }
            "rust" => {
                // Compile and run Rust code
                cmd.arg("bash")
                    .arg("-c")
                    .arg(format!(
                        "cd /work && rustc {} -o test_binary 2>&1 && ./test_binary 2>&1",
                        test_name
                    ));
            }
            _ => return Err(anyhow!("Unsupported language: {}", language)),
        }

        // Add additional arguments
        for arg in additional_args {
            cmd.arg(arg);
        }

        // Execute with timeout
        let output = cmd
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .output()
            .context("Failed to execute Docker command")?;

        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);

        Ok(TestResult {
            passed: output.status.success(),
            stdout: stdout.to_string(),
            stderr: stderr.to_string(),
            exit_code: output.status.code(),
        })
    }

    /// Compile TypeScript to JavaScript using esbuild in Docker
    pub fn compile_typescript(&self, ts_file: &Path) -> Result<PathBuf> {
        let test_dir = ts_file.parent()
            .ok_or_else(|| anyhow!("TypeScript file has no parent directory"))?;
        let ts_name = ts_file.file_name()
            .ok_or_else(|| anyhow!("TypeScript file has no name"))?
            .to_string_lossy();
        let js_name = ts_name.replace(".ts", ".js");
        let js_file = test_dir.join(&js_name);

        // Use esbuild to compile TypeScript
        let mut cmd = Command::new("npx");
        cmd.arg("esbuild")
            .arg(ts_file)
            .arg("--bundle")
            .arg("--platform=node")
            .arg("--target=node14")
            .arg("--format=cjs")
            .arg("--external:frame_runtime_ts")
            .arg(format!("--outfile={}", js_file.display()))
            .current_dir(test_dir);

        let output = cmd.output()
            .context("Failed to run esbuild")?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow!("TypeScript compilation failed: {}", stderr));
        }

        Ok(js_file)
    }

    /// Check if Docker is available and images exist
    pub fn verify_setup(&self, language: &str) -> Result<()> {
        // Check Docker is available
        let docker_check = Command::new("docker")
            .arg("--version")
            .output()
            .context("Docker not found. Please install Docker.")?;

        if !docker_check.status.success() {
            return Err(anyhow!("Docker command failed"));
        }

        // Check image exists
        let image = self.get_image_name(language);
        let image_check = Command::new("docker")
            .args(&["images", "-q", &image])
            .output()
            .context("Failed to check Docker images")?;

        let output = String::from_utf8_lossy(&image_check.stdout);
        if output.trim().is_empty() {
            return Err(anyhow!(
                "Docker image '{}' not found. Run build_images.sh to build it.", 
                image
            ));
        }

        Ok(())
    }
}

/// Result from Docker test execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestResult {
    pub passed: bool,
    pub stdout: String,
    pub stderr: String,
    pub exit_code: Option<i32>,
}

/// Integration with the test harness
pub struct DockerTestRunner {
    executor: DockerExecutor,
    framec_path: PathBuf,
}

impl DockerTestRunner {
    /// Create a new Docker test runner
    pub fn new(framec_path: PathBuf, shared_env_path: PathBuf) -> Self {
        let executor = DockerExecutor::new(shared_env_path, DockerConfig::default());
        Self {
            executor,
            framec_path,
        }
    }

    /// Transpile a Frame test file
    pub fn transpile(
        &self,
        test_file: &Path,
        language: &str,
        output_dir: &Path,
    ) -> Result<PathBuf> {
        let ext = match language {
            "python_3" | "python" => "py",
            "typescript" => "ts",
            "rust" => "rs",
            _ => return Err(anyhow!("Unsupported language: {}", language)),
        };

        let output_file = output_dir.join(format!(
            "{}.{}",
            test_file.file_stem()
                .ok_or_else(|| anyhow!("Test file has no stem"))?
                .to_string_lossy(),
            ext
        ));

        // Run framec to transpile
        let output = Command::new(&self.framec_path)
            .args(&["-l", language, test_file.to_str().unwrap()])
            .output()
            .context("Failed to run framec")?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow!("Transpilation failed: {}", stderr));
        }

        // Write transpiled code to file
        fs::write(&output_file, &output.stdout)
            .context("Failed to write transpiled file")?;

        Ok(output_file)
    }

    /// Run a complete test: transpile and execute in Docker
    pub fn run_test(&self, test_file: &Path, language: &str) -> Result<TestExecutionResult> {
        // Create temp directory for transpiled output
        let temp_dir = tempfile::tempdir()?;
        
        // Transpile the test
        let transpiled_file = self.transpile(test_file, language, temp_dir.path())?;
        
        // Special handling for TypeScript
        let exec_file = if language == "typescript" {
            self.executor.compile_typescript(&transpiled_file)?
        } else {
            transpiled_file
        };

        // Execute in Docker
        let result = self.executor.run_test(language, &exec_file, vec![])?;

        Ok(TestExecutionResult {
            test_file: test_file.to_path_buf(),
            language: language.to_string(),
            transpiled: true,
            executed: true,
            passed: result.passed,
            output: format!("{}\n{}", result.stdout, result.stderr),
            error: if result.passed { None } else { Some("Test failed".to_string()) },
        })
    }
}

/// Complete test execution result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestExecutionResult {
    pub test_file: PathBuf,
    pub language: String,
    pub transpiled: bool,
    pub executed: bool,
    pub passed: bool,
    pub output: String,
    pub error: Option<String>,
}