
// Tests nested interface calls with return values (Rust version)
// Note: Rust uses native return pattern


use std::collections::HashMap;

#[derive(Clone, Debug)]
struct SystemReturnReentrantTestFrameEvent {
    message: String,
}

impl SystemReturnReentrantTestFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct SystemReturnReentrantTestCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<SystemReturnReentrantTestFrameEvent>,
}

impl SystemReturnReentrantTestCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone, Default)]
struct StartContext {
    call_count: i32,
}

#[derive(Clone)]
enum SystemReturnReentrantTestStateContext {
    Start(StartContext),
    Empty,
}

impl Default for SystemReturnReentrantTestStateContext {
    fn default() -> Self {
        SystemReturnReentrantTestStateContext::Start(StartContext::default())
    }
}

pub struct SystemReturnReentrantTest {
    _state_stack: Vec<(String, SystemReturnReentrantTestStateContext)>,
    __compartment: SystemReturnReentrantTestCompartment,
    __next_compartment: Option<SystemReturnReentrantTestCompartment>,
    _sv_call_count: i32,
}

impl SystemReturnReentrantTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _sv_call_count: 0,
            __compartment: SystemReturnReentrantTestCompartment::new("Start"),
            __next_compartment: None,
        };
let __frame_event = SystemReturnReentrantTestFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: SystemReturnReentrantTestFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = SystemReturnReentrantTestFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = SystemReturnReentrantTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = SystemReturnReentrantTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &SystemReturnReentrantTestFrameEvent) {
match self.__compartment.state.as_str() {
    "Start" => self._state_Start(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: SystemReturnReentrantTestCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Start" => SystemReturnReentrantTestStateContext::Start(StartContext { call_count: self._sv_call_count }),
    _ => SystemReturnReentrantTestStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = SystemReturnReentrantTestFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    SystemReturnReentrantTestStateContext::Start(ctx) => {
        self._sv_call_count = ctx.call_count;
    }
    SystemReturnReentrantTestStateContext::Empty => {}
}
    }

    pub fn outer_call(&mut self) -> i32 {
let __e = SystemReturnReentrantTestFrameEvent::new("outer_call");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_outer_call(&__e),
            _ => Default::default(),
        }
    }

    pub fn inner_call(&mut self) -> i32 {
let __e = SystemReturnReentrantTestFrameEvent::new("inner_call");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_inner_call(&__e),
            _ => Default::default(),
        }
    }

    pub fn nested_call(&mut self) -> i32 {
let __e = SystemReturnReentrantTestFrameEvent::new("nested_call");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_nested_call(&__e),
            _ => Default::default(),
        }
    }

    pub fn get_call_count(&mut self) -> i32 {
let __e = SystemReturnReentrantTestFrameEvent::new("get_call_count");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_get_call_count(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Start(&mut self, __e: &SystemReturnReentrantTestFrameEvent) {
match __e.message.as_str() {
    "get_call_count" => { self._s_Start_get_call_count(__e); }
    "inner_call" => { self._s_Start_inner_call(__e); }
    "nested_call" => { self._s_Start_nested_call(__e); }
    "outer_call" => { self._s_Start_outer_call(__e); }
    "$>" => {
        self._sv_call_count = 0;
    }
    _ => {}
}
    }

    fn _s_Start_nested_call(&mut self, __e: &SystemReturnReentrantTestFrameEvent) -> i32 {
self._sv_call_count = self._sv_call_count + 1;
let result1: i32 = self.inner_call();
let result2: i32 = self.outer_call();
self._sv_call_count = self._sv_call_count + 1;
return 1000 + result1 + result2;
    }

    fn _s_Start_outer_call(&mut self, __e: &SystemReturnReentrantTestFrameEvent) -> i32 {
self._sv_call_count = self._sv_call_count + 1;
let inner_result: i32 = self.inner_call();
self._sv_call_count = self._sv_call_count + 1;
return 100 + inner_result;
    }

    fn _s_Start_inner_call(&mut self, __e: &SystemReturnReentrantTestFrameEvent) -> i32 {
self._sv_call_count = self._sv_call_count + 1;
return 10;
    }

    fn _s_Start_get_call_count(&mut self, __e: &SystemReturnReentrantTestFrameEvent) -> i32 {
return self._sv_call_count;
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
