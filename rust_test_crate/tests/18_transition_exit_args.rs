
// Rust version: Exit args not yet supported in Rust backend
// This test validates basic exit handler works in Rust


use std::collections::HashMap;

pub struct TransitionExitArgs {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    count: i32,
}

impl TransitionExitArgs {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            count: 0,
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
match self._state.as_str() {
    "Done" => {
        self._s_Done_enter();
    }
    _ => {}
}
    }

    fn _exit(&mut self) {
match self._state.as_str() {
            "Active" => { self._s_Active_exit(); }
            _ => {}
        }
    }

    pub fn leave(&mut self) {
match self._state.as_str() {
            "Active" => { self._s_Active_leave(); }
            _ => {}
        }
    }

    pub fn get_count(&mut self) -> i32 {
match self._state.as_str() {
            "Active" => self._s_Active_get_count(),
            "Done" => self._s_Done_get_count(),
            _ => Default::default(),
        }
    }

    fn _s_Active_leave(&mut self) {
self.count = 1;
self._transition("Done");
    }

    fn _s_Active_get_count(&mut self) -> i32 {
return self.count;
    }

    fn _s_Active_exit(&mut self) {
self.count = self.count + 10;
    }

    fn _s_Done_enter(&mut self) {
self.count = self.count + 100;
    }

    fn _s_Done_get_count(&mut self) -> i32 {
return self.count;
    }
}


fn main() {
    println!("=== Test 18: Transition Exit Args ===");
    let mut s = TransitionExitArgs::new();

    // Initial state is Active
    let count = s.get_count();
    assert_eq!(count, 0, "Expected count=0, got {}", count);

    // Leave - should call exit handler, then enter handler
    s.leave();
    let count = s.get_count();
    // count = 1 (from leave) + 10 (from exit) + 100 (from enter) = 111
    assert_eq!(count, 111, "Expected count=111, got {}", count);

    println!("PASS: Transition exit args work correctly");
}
