use std::collections::HashMap;

pub struct EventForwardTest {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    log: Vec<String>,
}

impl EventForwardTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            log: Vec::new(),
            _state: String::from("Idle"),
        };
        this._enter();
        this
    }

    fn _transition(&mut self, target_state: &str) {
        self._exit();
        self._state = target_state.to_string();
        self._enter();
    }

    fn _dispatch_event(&mut self, event: &str) {
let handler_name = format!("_s_{}_{}", self._state, event);
// Rust requires match-based dispatch or a handler registry
// For now, use explicit match in caller;
    }

    fn _enter(&mut self) {
        // No enter handlers
    }

    fn _exit(&mut self) {
        // No exit handlers
    }

    pub fn process(&mut self) {
match self._state.as_str() {
            "Idle" => { self._s_Idle_process(); }
            "Working" => { self._s_Working_process(); }
            _ => {}
        }
    }

    pub fn get_log(&mut self) -> Vec<String> {
match self._state.as_str() {
            "Idle" => self._s_Idle_get_log(),
            "Working" => self._s_Working_get_log(),
            _ => Default::default(),
        }
    }

    fn _s_Idle_get_log(&mut self) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Idle_process(&mut self) {
self.log.push("idle:process:before".to_string());
self._transition("Working");
return self._s_Working_process();
// This should NOT execute because -> => returns after dispatch
self.log.push("idle:process:after".to_string());
    }

    fn _s_Working_get_log(&mut self) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Working_process(&mut self) {
self.log.push("working:process".to_string());
    }
}


fn main() {
    println!("=== Test 19: Transition Forward (Rust) ===");
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
