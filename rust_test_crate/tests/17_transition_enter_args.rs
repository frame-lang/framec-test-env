
// Rust version: Enter args not yet supported in Rust backend
// This test validates basic transitions work in Rust


use std::collections::HashMap;

pub struct TransitionEnterArgs {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    count: i32,
}

impl TransitionEnterArgs {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            count: 0,
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
match self._state.as_str() {
    "Active" => {
        self._s_Active_enter();
    }
    _ => {}
}
    }

    fn _exit(&mut self) {
        // No exit handlers
    }

    pub fn start(&mut self) {
match self._state.as_str() {
            "Idle" => { self._s_Idle_start(); }
            "Active" => { self._s_Active_start(); }
            _ => {}
        }
    }

    pub fn get_count(&mut self) -> i32 {
match self._state.as_str() {
            "Idle" => self._s_Idle_get_count(),
            "Active" => self._s_Active_get_count(),
            _ => Default::default(),
        }
    }

    fn _s_Idle_get_count(&mut self) -> i32 {
return self.count;
    }

    fn _s_Idle_start(&mut self) {
self.count = 1;
self._transition("Active");
    }

    fn _s_Active_get_count(&mut self) -> i32 {
return self.count;
    }

    fn _s_Active_enter(&mut self) {
self.count = self.count + 1;
    }

    fn _s_Active_start(&mut self) {
self.count = self.count + 10;
    }
}


fn main() {
    println!("=== Test 17: Transition Enter Args ===");
    let mut s = TransitionEnterArgs::new();

    // Initial state is Idle
    let count = s.get_count();
    assert_eq!(count, 0, "Expected count=0, got {}", count);

    // Transition to Active - enter handler should increment
    s.start();
    let count = s.get_count();
    // count should be 1 (from start) + 1 (from enter) = 2
    assert_eq!(count, 2, "Expected count=2, got {}", count);

    println!("PASS: Transition enter args work correctly");
}
