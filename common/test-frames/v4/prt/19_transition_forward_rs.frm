@@target rust

@@system EventForwardTest {
    interface:
        process()
        get_log(): Vec<String>

    domain:
        var log: Vec<String> = Vec::new()

    machine:
        $Idle {
            process() {
                self.log.push("idle:process:before".to_string());
                -> => $Working
                // This should NOT execute because -> => returns after dispatch
                self.log.push("idle:process:after".to_string());
            }

            get_log(): Vec<String> {
                return self.log.clone();
            }
        }

        $Working {
            process() {
                self.log.push("working:process".to_string());
            }

            get_log(): Vec<String> {
                return self.log.clone();
            }
        }
}

fn main() {
    println!("=== Test 16: Transition Forward (Rust) ===");
    let mut s = EventForwardTest::new();
    s.process();
    let log = s.get_log();
    println!("Log: {:?}", log);

    // After transition-forward:
    // - Idle logs "idle:process:before"
    // - Transition to Working
    // - Working handles process(), logs "working:process"
    // - Return prevents "idle:process:after"
    assert!(log.contains(&"idle:process:before".to_string()), "Expected 'idle:process:before' in log: {:?}", log);
    assert!(log.contains(&"working:process".to_string()), "Expected 'working:process' in log: {:?}", log);
    assert!(!log.contains(&"idle:process:after".to_string()), "Should NOT have 'idle:process:after' in log: {:?}", log);

    println!("PASS: Transition forward works correctly");
}
