
fn helper_function(x: i32) -> i32 {
    x * 2
}


use std::collections::HashMap;

pub struct NativeCode {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
}

impl NativeCode {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            _state: String::from("Active"),
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

    pub fn compute(&mut self, value: i32) -> i32 {
match self._state.as_str() {
            "Active" => self._s_Active_compute(value),
            _ => Default::default(),
        }
    }

    pub fn use_math(&mut self) -> f64 {
match self._state.as_str() {
            "Active" => self._s_Active_use_math(),
            _ => Default::default(),
        }
    }

    fn _s_Active_use_math(&mut self) -> f64 {
// Using standard math operations
let result = (16.0_f64).sqrt() + std::f64::consts::PI;
println!("Math result: {}", result);
result
    }

    fn _s_Active_compute(&mut self, value: i32) -> i32 {
// Native code with local variables
let temp = value + 10;
let result = helper_function(temp);
println!("Computed: {} -> {}", value, result);
result
    }
}


fn main() {
    println!("=== Test 04: Native Code Preservation ===");
    let mut s = NativeCode::new();

    // Test native code in handler with helper function
    let result = s.compute(5);
    let expected = (5 + 10) * 2;  // 30
    assert_eq!(result, expected, "Expected {}, got {}", expected, result);
    println!("compute(5) = {}", result);

    // Test math operations
    let math_result = s.use_math();
    let expected_math = (16.0_f64).sqrt() + std::f64::consts::PI;
    assert!((math_result - expected_math).abs() < 0.001, "Expected ~{}, got {}", expected_math, math_result);
    println!("use_math() = {}", math_result);

    println!("PASS: Native code preservation works correctly");
}
