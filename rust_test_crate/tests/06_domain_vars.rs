use std::collections::HashMap;

pub struct DomainVars {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    count: i32,
    name: String,
}

impl DomainVars {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            count: 0,
            name: String::from("counter"),
            _state: String::from("Counting"),
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

    pub fn increment(&mut self) {
match self._state.as_str() {
            "Counting" => { self._s_Counting_increment(); }
            _ => {}
        }
    }

    pub fn decrement(&mut self) {
match self._state.as_str() {
            "Counting" => { self._s_Counting_decrement(); }
            _ => {}
        }
    }

    pub fn get_count(&mut self) -> i32 {
match self._state.as_str() {
            "Counting" => self._s_Counting_get_count(),
            _ => Default::default(),
        }
    }

    pub fn set_count(&mut self, value: i32) {
match self._state.as_str() {
            "Counting" => { self._s_Counting_set_count(value); }
            _ => {}
        }
    }

    fn _s_Counting_increment(&mut self) {
self.count += 1;
println!("{}: incremented to {}", self.name, self.count);
    }

    fn _s_Counting_get_count(&mut self) -> i32 {
self.count
    }

    fn _s_Counting_decrement(&mut self) {
self.count -= 1;
println!("{}: decremented to {}", self.name, self.count);
    }

    fn _s_Counting_set_count(&mut self, value: i32) {
self.count = value;
println!("{}: set to {}", self.name, self.count);
    }
}


fn main() {
    println!("=== Test 06: Domain Variables ===");
    let mut s = DomainVars::new();

    // Initial value should be 0
    let count = s.get_count();
    assert_eq!(count, 0, "Expected initial count=0, got {}", count);
    println!("Initial count: {}", count);

    // Increment
    s.increment();
    let count = s.get_count();
    assert_eq!(count, 1, "Expected count=1, got {}", count);

    s.increment();
    let count = s.get_count();
    assert_eq!(count, 2, "Expected count=2, got {}", count);

    // Decrement
    s.decrement();
    let count = s.get_count();
    assert_eq!(count, 1, "Expected count=1, got {}", count);

    // Set directly
    s.set_count(100);
    let count = s.get_count();
    assert_eq!(count, 100, "Expected count=100, got {}", count);

    println!("Final count: {}", count);
    println!("PASS: Domain variables work correctly");
}
