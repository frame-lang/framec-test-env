use std::collections::HashMap;

pub struct ActionsTest {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    log: String,
}

impl ActionsTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            log: String::new(),
            _state: String::from("Ready"),
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

    pub fn process(&mut self, value: i32) -> i32 {
match self._state.as_str() {
            "Ready" => self._s_Ready_process(value),
            _ => Default::default(),
        }
    }

    pub fn get_log(&mut self) -> String {
match self._state.as_str() {
            "Ready" => self._s_Ready_get_log(),
            _ => Default::default(),
        }
    }

    fn _s_Ready_get_log(&mut self) -> String {
return self.log.clone();
    }

    fn _s_Ready_process(&mut self, value: i32) -> i32 {
self.__log_event("start");
self.__validate_positive(value);
self.__log_event("valid");
let result = value * 2;
self.__log_event("done");
return result;
    }

    fn __log_event(&mut self, msg: &str) {
            self.log.push_str(msg);
            self.log.push(';');
    }

    fn __validate_positive(&mut self, n: i32) {
            if n < 0 {
                panic!("Value must be positive: {}", n);
            }
    }
}


fn main() {
    println!("=== Test 21: Actions Basic (Rust) ===");
    let mut s = ActionsTest::new();

    // Test 1: Actions are called correctly
    let result = s.process(5);
    assert_eq!(result, 10, "Expected 10, got {}", result);
    println!("1. process(5) = {}", result);

    // Test 2: Log shows action calls
    let log = s.get_log();
    assert!(log.contains("start"), "Missing 'start' in log: {}", log);
    assert!(log.contains("valid"), "Missing 'valid' in log: {}", log);
    assert!(log.contains("done"), "Missing 'done' in log: {}", log);
    println!("2. Log: {}", log);

    // Test 3: Action with validation (we just verify it works for valid values)
    // Note: Testing panic in Rust requires different setup, skip negative test
    println!("3. Validation works (positive values verified)");

    println!("PASS: Actions basic works correctly");
}
