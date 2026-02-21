
// Tests basic system.return functionality in Rust
// Note: Rust uses native return, not _return_value pattern


use std::collections::HashMap;

#[derive(Clone, Debug)]
struct SystemReturnDefaultTestFrameEvent {
    message: String,
}

impl SystemReturnDefaultTestFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct SystemReturnDefaultTestCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<SystemReturnDefaultTestFrameEvent>,
}

impl SystemReturnDefaultTestCompartment {
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
    count: i32,
}

#[derive(Clone)]
enum SystemReturnDefaultTestStateContext {
    Start(StartContext),
    Empty,
}

impl Default for SystemReturnDefaultTestStateContext {
    fn default() -> Self {
        SystemReturnDefaultTestStateContext::Start(StartContext::default())
    }
}

pub struct SystemReturnDefaultTest {
    _state_stack: Vec<(String, SystemReturnDefaultTestStateContext)>,
    __compartment: SystemReturnDefaultTestCompartment,
    __next_compartment: Option<SystemReturnDefaultTestCompartment>,
    _sv_count: i32,
}

impl SystemReturnDefaultTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _sv_count: 0,
            __compartment: SystemReturnDefaultTestCompartment::new("Start"),
            __next_compartment: None,
        };
let __frame_event = SystemReturnDefaultTestFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: SystemReturnDefaultTestFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = SystemReturnDefaultTestFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = SystemReturnDefaultTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = SystemReturnDefaultTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &SystemReturnDefaultTestFrameEvent) {
match self.__compartment.state.as_str() {
    "Start" => self._state_Start(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: SystemReturnDefaultTestCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Start" => SystemReturnDefaultTestStateContext::Start(StartContext { count: self._sv_count }),
    _ => SystemReturnDefaultTestStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = SystemReturnDefaultTestFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    SystemReturnDefaultTestStateContext::Start(ctx) => {
        self._sv_count = ctx.count;
    }
    SystemReturnDefaultTestStateContext::Empty => {}
}
    }

    pub fn handler_sets_value(&mut self) -> i32 {
let __e = SystemReturnDefaultTestFrameEvent::new("handler_sets_value");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_handler_sets_value(&__e),
            _ => Default::default(),
        }
    }

    pub fn handler_returns_computed(&mut self) -> i32 {
let __e = SystemReturnDefaultTestFrameEvent::new("handler_returns_computed");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_handler_returns_computed(&__e),
            _ => Default::default(),
        }
    }

    pub fn get_count(&mut self) -> i32 {
let __e = SystemReturnDefaultTestFrameEvent::new("get_count");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_get_count(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Start(&mut self, __e: &SystemReturnDefaultTestFrameEvent) {
match __e.message.as_str() {
    "get_count" => { self._s_Start_get_count(__e); }
    "handler_returns_computed" => { self._s_Start_handler_returns_computed(__e); }
    "handler_sets_value" => { self._s_Start_handler_sets_value(__e); }
    "$>" => {
        self._sv_count = 0;
    }
    _ => {}
}
    }

    fn _s_Start_handler_sets_value(&mut self, __e: &SystemReturnDefaultTestFrameEvent) -> i32 {
return 42;
    }

    fn _s_Start_handler_returns_computed(&mut self, __e: &SystemReturnDefaultTestFrameEvent) -> i32 {
self._sv_count = self._sv_count + 1;
return self._sv_count;
    }

    fn _s_Start_get_count(&mut self, __e: &SystemReturnDefaultTestFrameEvent) -> i32 {
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
