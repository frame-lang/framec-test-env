use std::collections::HashMap;

pub struct WithParams {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    total: i32,
}

impl WithParams {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            total: 0,
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

    pub fn start(&mut self, initial: i32) {
match self._state.as_str() {
            "Idle" => { self._s_Idle_start(initial); }
            "Running" => { self._s_Running_start(initial); }
            _ => {}
        }
    }

    pub fn add(&mut self, value: i32) {
match self._state.as_str() {
            "Idle" => { self._s_Idle_add(value); }
            "Running" => { self._s_Running_add(value); }
            _ => {}
        }
    }

    pub fn multiply(&mut self, a: i32, b: i32) -> i32 {
match self._state.as_str() {
            "Idle" => self._s_Idle_multiply(a, b),
            "Running" => self._s_Running_multiply(a, b),
            _ => Default::default(),
        }
    }

    pub fn get_total(&mut self) -> i32 {
match self._state.as_str() {
            "Idle" => self._s_Idle_get_total(),
            "Running" => self._s_Running_get_total(),
            _ => Default::default(),
        }
    }

    fn _s_Idle_add(&mut self, value: i32) {
println!("Cannot add in Idle state");
    }

    fn _s_Idle_start(&mut self, initial: i32) {
self.total = initial;
println!("Started with initial value: {}", initial);
self._transition("Running");
    }

    fn _s_Idle_get_total(&mut self) -> i32 {
self.total
    }

    fn _s_Idle_multiply(&mut self, a: i32, b: i32) -> i32 {
0
    }

    fn _s_Running_get_total(&mut self) -> i32 {
self.total
    }

    fn _s_Running_multiply(&mut self, a: i32, b: i32) -> i32 {
let result = a * b;
self.total += result;
println!("Multiplied {} * {} = {}, total is now {}", a, b, result, self.total);
result
    }

    fn _s_Running_start(&mut self, initial: i32) {
println!("Already running");
    }

    fn _s_Running_add(&mut self, value: i32) {
self.total += value;
println!("Added {}, total is now {}", value, self.total);
    }
}


fn main() {
    println!("=== Test 07: Handler Parameters ===");
    let mut s = WithParams::new();

    // Initial total should be 0
    let total = s.get_total();
    assert_eq!(total, 0, "Expected initial total=0, got {}", total);

    // Start with initial value
    s.start(100);
    let total = s.get_total();
    assert_eq!(total, 100, "Expected total=100, got {}", total);
    println!("After start(100): total = {}", total);

    // Add value
    s.add(25);
    let total = s.get_total();
    assert_eq!(total, 125, "Expected total=125, got {}", total);
    println!("After add(25): total = {}", total);

    // Multiply with two params
    let result = s.multiply(3, 5);
    assert_eq!(result, 15, "Expected multiply result=15, got {}", result);
    let total = s.get_total();
    assert_eq!(total, 140, "Expected total=140, got {}", total);
    println!("After multiply(3,5): result = {}, total = {}", result, total);

    println!("PASS: Handler parameters work correctly");
}
