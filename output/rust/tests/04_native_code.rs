
fn helper_function(x: i32) -> i32 {
    x * 2
}


use std::collections::HashMap;

#[derive(Clone, Debug)]
struct NativeCodeFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, String>,
}

impl NativeCodeFrameEvent {
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

struct NativeCodeFrameContext {
    event: NativeCodeFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl NativeCodeFrameContext {
    fn new(event: NativeCodeFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct NativeCodeCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<NativeCodeFrameEvent>,
}

impl NativeCodeCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum NativeCodeStateContext {
    Active,
    Empty,
}

impl Default for NativeCodeStateContext {
    fn default() -> Self {
        NativeCodeStateContext::Active
    }
}

pub struct NativeCode {
    _state_stack: Vec<(String, NativeCodeStateContext)>,
    __compartment: NativeCodeCompartment,
    __next_compartment: Option<NativeCodeCompartment>,
    _context_stack: Vec<NativeCodeFrameContext>,
}

impl NativeCode {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            __compartment: NativeCodeCompartment::new("Active"),
            __next_compartment: None,
        };
let __frame_event = NativeCodeFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: NativeCodeFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = NativeCodeFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = NativeCodeFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = NativeCodeFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &NativeCodeFrameEvent) {
match self.__compartment.state.as_str() {
    "Active" => self._state_Active(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: NativeCodeCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Active" => NativeCodeStateContext::Active,
    _ => NativeCodeStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = NativeCodeFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    NativeCodeStateContext::Active => {}
    NativeCodeStateContext::Empty => {}
}
    }

    pub fn compute(&mut self, value: i32) -> i32 {
let __e = NativeCodeFrameEvent::new("compute");
match self.__compartment.state.as_str() {
            "Active" => self._s_Active_compute(&__e, value),
            _ => Default::default(),
        }
    }

    pub fn use_math(&mut self) -> f64 {
let __e = NativeCodeFrameEvent::new("use_math");
match self.__compartment.state.as_str() {
            "Active" => self._s_Active_use_math(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Active(&mut self, __e: &NativeCodeFrameEvent) {
match __e.message.as_str() {
    "use_math" => { self._s_Active_use_math(__e); }
    _ => {}
}
    }

    fn _s_Active_compute(&mut self, __e: &NativeCodeFrameEvent, value: i32) -> i32 {
// Native code with local variables
let temp = value + 10;
let result = helper_function(temp);
println!("Computed: {} -> {}", value, result);
result
    }

    fn _s_Active_use_math(&mut self, __e: &NativeCodeFrameEvent) -> f64 {
// Using standard math operations
let result = (16.0_f64).sqrt() + std::f64::consts::PI;
println!("Math result: {}", result);
result
    }
}


fn main() {
    println!("=== Test 04: Native Code Preservation ===");
    let mut s = NativeCode::new();

    // Test native code in handler with helper function
    let result = s.compute(5);
    let expected = (5 + 10) * 2;  // 30
    assert_eq!(result, expected, "Expected {}, got {}", expected, result);
    println!("compute(5) = {}", result);

    // Test math operations
    let math_result = s.use_math();
    let expected_math = (16.0_f64).sqrt() + std::f64::consts::PI;
    assert!((math_result - expected_math).abs() < 0.001, "Expected ~{}, got {}", expected_math, math_result);
    println!("use_math() = {}", math_result);

    println!("PASS: Native code preservation works correctly");
}
