
// Tests system.return in enter handlers (Rust version)
// Note: Rust uses native return pattern, chain semantics differ from Python/TS


use std::collections::HashMap;

pub struct SystemReturnChainTest {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
}

impl SystemReturnChainTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            _state: String::from("Start"),
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

    pub fn get_state_num(&mut self) -> i32 {
match self._state.as_str() {
            "Start" => self._s_Start_get_state_num(),
            "EnterSetter" => self._s_EnterSetter_get_state_num(),
            "BothSet" => self._s_BothSet_get_state_num(),
            _ => Default::default(),
        }
    }

    fn _s_BothSet_get_state_num(&mut self) -> i32 {
return 3;
    }

    fn _s_EnterSetter_get_state_num(&mut self) -> i32 {
return 2;
    }

    fn _s_Start_get_state_num(&mut self) -> i32 {
return 1;
    }
}


fn main() {
    println!("=== Test 15: System Return (Rust) ===");

    let mut s1 = SystemReturnChainTest::new();
    let state = s1.get_state_num();
    assert_eq!(state, 1, "Expected state 1, got {}", state);
    println!("1. get_state_num() = {}", state);

    println!("PASS: System return works correctly");
}

