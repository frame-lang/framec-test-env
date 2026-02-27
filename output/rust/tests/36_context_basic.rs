
// Test: Basic System Context Access
// Validates @@.param, @@:return, @@:event syntax


use std::collections::HashMap;

#[derive(Clone, Debug)]
struct ContextBasicTestFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, String>,
}

impl ContextBasicTestFrameEvent {
    fn new(message: &str) -> Self {
        Self {
            message: message.to_string(),
            parameters: std::collections::HashMap::new(),
        }
    }
    fn with_parameters(message: &str, parameters: std::collections::HashMap<String, String>) -> Self {
        Self { message: message.to_string(), parameters }
    }
}

struct ContextBasicTestFrameContext {
    event: ContextBasicTestFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl ContextBasicTestFrameContext {
    fn new(event: ContextBasicTestFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct ContextBasicTestCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<ContextBasicTestFrameEvent>,
}

impl ContextBasicTestCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum ContextBasicTestStateContext {
    Ready,
    Empty,
}

impl Default for ContextBasicTestStateContext {
    fn default() -> Self {
        ContextBasicTestStateContext::Ready
    }
}

pub struct ContextBasicTest {
    _state_stack: Vec<(String, ContextBasicTestStateContext)>,
    __compartment: ContextBasicTestCompartment,
    __next_compartment: Option<ContextBasicTestCompartment>,
    _context_stack: Vec<ContextBasicTestFrameContext>,
}

impl ContextBasicTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            __compartment: ContextBasicTestCompartment::new("Ready"),
            __next_compartment: None,
        };
let __frame_event = ContextBasicTestFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: ContextBasicTestFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = ContextBasicTestFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = ContextBasicTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = ContextBasicTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &ContextBasicTestFrameEvent) {
match self.__compartment.state.as_str() {
    "Ready" => self._state_Ready(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: ContextBasicTestCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Ready" => ContextBasicTestStateContext::Ready,
    _ => ContextBasicTestStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = ContextBasicTestFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    ContextBasicTestStateContext::Ready => {}
    ContextBasicTestStateContext::Empty => {}
}
    }

    pub fn add(&mut self, a: i32, b: i32) -> i32 {
let __e = ContextBasicTestFrameEvent::new("add");
match self.__compartment.state.as_str() {
            "Ready" => self._s_Ready_add(&__e, a, b),
            _ => Default::default(),
        }
    }

    pub fn get_event_name(&mut self) -> String {
let __e = ContextBasicTestFrameEvent::new("get_event_name");
match self.__compartment.state.as_str() {
            "Ready" => self._s_Ready_get_event_name(&__e),
            _ => Default::default(),
        }
    }

    pub fn greet(&mut self, name: String) -> String {
let __e = ContextBasicTestFrameEvent::new("greet");
match self.__compartment.state.as_str() {
            "Ready" => self._s_Ready_greet(&__e, name),
            _ => Default::default(),
        }
    }

    fn _state_Ready(&mut self, __e: &ContextBasicTestFrameEvent) {
match __e.message.as_str() {
    "get_event_name" => { self._s_Ready_get_event_name(__e); }
    _ => {}
}
    }

    fn _s_Ready_get_event_name(&mut self, __e: &ContextBasicTestFrameEvent) -> String {
// Access event name
return /* @@:event */.to_string();
    }

    fn _s_Ready_greet(&mut self, __e: &ContextBasicTestFrameEvent, name: String) -> String {
// Mix param access and return
let result = format!("Hello, {}!", /* @@.name - context params not implemented for Rust */);
return result;
    }

    fn _s_Ready_add(&mut self, __e: &ContextBasicTestFrameEvent, a: i32, b: i32) -> i32 {
// Access params via @@ shorthand
return /* @@.a */ + /* @@.b */;
    }
}


fn main() {
    println!("=== Test 36: Context Basic ===");
    let mut s = ContextBasicTest::new();

    // Test 1: @@.a and @@.b param access, @@:return
    let result1 = s.add(3, 5);
    assert_eq!(result1, 8, "Expected 8, got {}", result1);
    println!("1. add(3, 5) = {}", result1);

    // Test 2: @@:event access
    let event_name = s.get_event_name();
    assert_eq!(event_name, "get_event_name", "Expected 'get_event_name', got '{}'", event_name);
    println!("2. @@:event = '{}'", event_name);

    // Test 3: @@.name param access with string
    let greeting = s.greet("World".to_string());
    assert_eq!(greeting, "Hello, World!", "Expected 'Hello, World!', got '{}'", greeting);
    println!("3. greet('World') = '{}'", greeting);

    println!("PASS: Context basic access works correctly");
}
