use std::collections::HashMap;

pub struct WithTransition {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
}

impl WithTransition {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            _state: String::from("First"),
        };
        this._enter();
        this
    }

    fn _transition(&mut self, target_state: &str) {
        self._exit();
        self._state = target_state.to_string();
        self._enter();
    }

    fn _change_state(&mut self, target_state: &str) {
        self._state = target_state.to_string();
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

    pub fn next(&mut self) {
match self._state.as_str() {
            "First" => { self._s_First_next(); }
            "Second" => { self._s_Second_next(); }
            _ => {}
        }
    }

    pub fn get_state(&mut self) -> String {
match self._state.as_str() {
            "First" => self._s_First_get_state(),
            "Second" => self._s_Second_get_state(),
            _ => Default::default(),
        }
    }

    fn _s_Second_next(&mut self) {
println!("Transitioning: Second -> First");
self._transition("First");
    }

    fn _s_Second_get_state(&mut self) -> String {
"Second".to_string()
    }

    fn _s_First_get_state(&mut self) -> String {
"First".to_string()
    }

    fn _s_First_next(&mut self) {
println!("Transitioning: First -> Second");
self._transition("Second");
    }
}


fn main() {
    println!("=== Test 03: State Transitions ===");
    let mut s = WithTransition::new();

    // Initial state should be First
    let state = s.get_state();
    assert_eq!(state, "First", "Expected 'First', got '{}'", state);
    println!("Initial state: {}", state);

    // Transition to Second
    s.next();
    let state = s.get_state();
    assert_eq!(state, "Second", "Expected 'Second', got '{}'", state);
    println!("After first next(): {}", state);

    // Transition back to First
    s.next();
    let state = s.get_state();
    assert_eq!(state, "First", "Expected 'First', got '{}'", state);
    println!("After second next(): {}", state);

    println!("PASS: State transitions work correctly");
}

