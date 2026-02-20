
// Tests nested interface calls with return values (Rust version)
// Note: Rust uses native return pattern


use std::collections::HashMap;

#[derive(Clone, Default)]
struct StartContext {
    call_count: i32,
}

#[derive(Clone)]
enum SystemReturnReentrantTestCompartment {
    Start(StartContext),
    Empty,
}

impl Default for SystemReturnReentrantTestCompartment {
    fn default() -> Self {
        SystemReturnReentrantTestCompartment::Start(StartContext::default())
    }
}

pub struct SystemReturnReentrantTest {
    _state: String,
    _state_stack: Vec<(String, SystemReturnReentrantTestCompartment)>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    _sv_call_count: i32,
}

impl SystemReturnReentrantTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            _sv_call_count: 0,
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
        self._sv_call_count = 0;
    }
    _ => {}
}
    }

    fn _exit(&mut self) {
        // No exit handlers
    }

    fn _state_stack_push(&mut self) {
let compartment = match self._state.as_str() {
    "Start" => SystemReturnReentrantTestCompartment::Start(StartContext { call_count: self._sv_call_count }),
    _ => SystemReturnReentrantTestCompartment::Empty,
};
self._state_stack.push((self._state.clone(), compartment));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, compartment) = self._state_stack.pop().unwrap();
self._exit();
self._state = saved_state;
match compartment {
    SystemReturnReentrantTestCompartment::Start(ctx) => {
        self._sv_call_count = ctx.call_count;
    }
    SystemReturnReentrantTestCompartment::Empty => {}
}
    }

    pub fn outer_call(&mut self) -> i32 {
match self._state.as_str() {
            "Start" => self._s_Start_outer_call(),
            _ => Default::default(),
        }
    }

    pub fn inner_call(&mut self) -> i32 {
match self._state.as_str() {
            "Start" => self._s_Start_inner_call(),
            _ => Default::default(),
        }
    }

    pub fn nested_call(&mut self) -> i32 {
match self._state.as_str() {
            "Start" => self._s_Start_nested_call(),
            _ => Default::default(),
        }
    }

    pub fn get_call_count(&mut self) -> i32 {
match self._state.as_str() {
            "Start" => self._s_Start_get_call_count(),
            _ => Default::default(),
        }
    }

    fn _s_Start_get_call_count(&mut self) -> i32 {
return self._sv_call_count;
    }

    fn _s_Start_outer_call(&mut self) -> i32 {
self._sv_call_count = self._sv_call_count + 1;
let inner_result: i32 = self.inner_call();
self._sv_call_count = self._sv_call_count + 1;
return 100 + inner_result;
    }

    fn _s_Start_inner_call(&mut self) -> i32 {
self._sv_call_count = self._sv_call_count + 1;
return 10;
    }

    fn _s_Start_nested_call(&mut self) -> i32 {
self._sv_call_count = self._sv_call_count + 1;
let result1: i32 = self.inner_call();
let result2: i32 = self.outer_call();
self._sv_call_count = self._sv_call_count + 1;
return 1000 + result1 + result2;
    }
}


fn main() {
    println!("=== Test 16: System Return Reentrant (Nested Calls) ===");

    // Test 1: Simple inner call
    let mut s1 = SystemReturnReentrantTest::new();
    let result = s1.inner_call();
    assert_eq!(result, 10, "Expected 10, got {}", result);
    println!("1. inner_call() = {}", result);

    // Test 2: Outer calls inner - contexts should be separate
    let mut s2 = SystemReturnReentrantTest::new();
    let result = s2.outer_call();
    // outer returns 100 + inner's 10 = 110
    assert_eq!(result, 110, "Expected 110, got {}", result);
    let count = s2.get_call_count();
    assert_eq!(count, 3, "Expected 3 calls, got {}", count);
    println!("2. outer_call() = {} (call_count = {})", result, count);

    // Test 3: Deeply nested calls
    let mut s3 = SystemReturnReentrantTest::new();
    let result = s3.nested_call();
    // nested: 1000 + inner(10) + outer(100 + inner(10)) = 1000 + 10 + 110 = 1120
    assert_eq!(result, 1120, "Expected 1120, got {}", result);
    let count = s3.get_call_count();
    assert_eq!(count, 6, "Expected 6 calls, got {}", count);
    println!("3. nested_call() = {} (call_count = {})", result, count);

    println!("PASS: System return reentrant (nested calls) works correctly");
}
