
// Tests basic system.return functionality in Rust
// Note: Rust uses native return, not _return_value pattern


use std::collections::HashMap;

#[derive(Clone, Default)]
struct StartContext {
    count: i32,
}

#[derive(Clone)]
enum SystemReturnDefaultTestCompartment {
    Start(StartContext),
    Empty,
}

impl Default for SystemReturnDefaultTestCompartment {
    fn default() -> Self {
        SystemReturnDefaultTestCompartment::Start(StartContext::default())
    }
}

pub struct SystemReturnDefaultTest {
    _state: String,
    _state_stack: Vec<(String, SystemReturnDefaultTestCompartment)>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    _sv_count: i32,
}

impl SystemReturnDefaultTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            _sv_count: 0,
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

    fn _dispatch_event(&mut self, event: &str) {
let handler_name = format!("_s_{}_{}", self._state, event);
// Rust requires match-based dispatch or a handler registry
// For now, use explicit match in caller;
    }

    fn _enter(&mut self) {
match self._state.as_str() {
    "Start" => {
        self._sv_count = 0;
    }
    _ => {}
}
    }

    fn _exit(&mut self) {
        // No exit handlers
    }

    fn _state_stack_push(&mut self) {
let compartment = match self._state.as_str() {
    "Start" => SystemReturnDefaultTestCompartment::Start(StartContext { count: self._sv_count }),
    _ => SystemReturnDefaultTestCompartment::Empty,
};
self._state_stack.push((self._state.clone(), compartment));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, compartment) = self._state_stack.pop().unwrap();
self._exit();
self._state = saved_state;
match compartment {
    SystemReturnDefaultTestCompartment::Start(ctx) => {
        self._sv_count = ctx.count;
    }
    SystemReturnDefaultTestCompartment::Empty => {}
}
    }

    pub fn handler_sets_value(&mut self) -> i32 {
match self._state.as_str() {
            "Start" => self._s_Start_handler_sets_value(),
            _ => Default::default(),
        }
    }

    pub fn handler_returns_computed(&mut self) -> i32 {
match self._state.as_str() {
            "Start" => self._s_Start_handler_returns_computed(),
            _ => Default::default(),
        }
    }

    pub fn get_count(&mut self) -> i32 {
match self._state.as_str() {
            "Start" => self._s_Start_get_count(),
            _ => Default::default(),
        }
    }

    fn _s_Start_handler_returns_computed(&mut self) -> i32 {
self._sv_count = self._sv_count + 1;
return self._sv_count;
    }

    fn _s_Start_handler_sets_value(&mut self) -> i32 {
return 42;
    }

    fn _s_Start_get_count(&mut self) -> i32 {
return self._sv_count;
    }
}


fn main() {
    println!("=== Test 14: System Return Behavior ===");
    let mut s = SystemReturnDefaultTest::new();

    // Test 1: Handler explicitly sets return value
    let result = s.handler_sets_value();
    assert_eq!(result, 42, "Expected 42, got {}", result);
    println!("1. handler_sets_value() = {}", result);

    // Test 2: Handler computes and returns value
    let result = s.handler_returns_computed();
    assert_eq!(result, 1, "Expected 1, got {}", result);
    println!("2. handler_returns_computed() = {}", result);

    // Test 3: Verify side effect
    let count = s.get_count();
    assert_eq!(count, 1, "Expected count=1, got {}", count);
    println!("3. get_count() = {}", count);

    // Test 4: Call again
    let result = s.handler_returns_computed();
    assert_eq!(result, 2, "Expected 2, got {}", result);
    println!("4. handler_returns_computed() again = {}", result);

    println!("PASS: System return behavior works correctly");
}
