use std::collections::HashMap;

pub struct WithInterface {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    call_count: i32,
}

impl WithInterface {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            call_count: 0,
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

    pub fn greet(&mut self, name: &str) -> String {
match self._state.as_str() {
            "Ready" => self._s_Ready_greet(name),
            _ => Default::default(),
        }
    }

    pub fn get_count(&mut self) -> i32 {
match self._state.as_str() {
            "Ready" => self._s_Ready_get_count(),
            _ => Default::default(),
        }
    }

    fn _s_Ready_get_count(&mut self) -> i32 {
self.call_count
    }

    fn _s_Ready_greet(&mut self, name: &str) -> String {
self.call_count += 1;
format!("Hello, {}!", name)
    }
}


fn main() {
    println!("=== Test 02: Interface Methods ===");
    let mut s = WithInterface::new();

    // Test interface method with parameter and return
    let result = s.greet("World");
    assert_eq!(result, "Hello, World!", "Expected 'Hello, World!', got '{}'", result);
    println!("greet('World') = {}", result);

    // Test domain variable access through interface
    let count = s.get_count();
    assert_eq!(count, 1, "Expected count=1, got {}", count);
    println!("get_count() = {}", count);

    // Call again to verify state
    s.greet("Frame");
    let count2 = s.get_count();
    assert_eq!(count2, 2, "Expected count=2, got {}", count2);
    println!("After second call: get_count() = {}", count2);

    println!("PASS: Interface methods work correctly");
}
