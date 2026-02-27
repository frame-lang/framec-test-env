
use std::collections::HashMap;

// Test: Context Data (@@:data)
// Validates call-scoped data that persists across handler -> <$ -> $> chain


use std::collections::HashMap;

#[derive(Clone, Debug)]
struct ContextDataTestFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, String>,
}

impl ContextDataTestFrameEvent {
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

struct ContextDataTestFrameContext {
    event: ContextDataTestFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl ContextDataTestFrameContext {
    fn new(event: ContextDataTestFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct ContextDataTestCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<ContextDataTestFrameEvent>,
}

impl ContextDataTestCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum ContextDataTestStateContext {
    Start,
    End,
    Empty,
}

impl Default for ContextDataTestStateContext {
    fn default() -> Self {
        ContextDataTestStateContext::Start
    }
}

pub struct ContextDataTest {
    _state_stack: Vec<(String, ContextDataTestStateContext)>,
    __compartment: ContextDataTestCompartment,
    __next_compartment: Option<ContextDataTestCompartment>,
    _context_stack: Vec<ContextDataTestFrameContext>,
}

impl ContextDataTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            __compartment: ContextDataTestCompartment::new("Start"),
            __next_compartment: None,
        };
let __frame_event = ContextDataTestFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: ContextDataTestFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = ContextDataTestFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = ContextDataTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = ContextDataTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &ContextDataTestFrameEvent) {
match self.__compartment.state.as_str() {
    "Start" => self._state_Start(__e),
    "End" => self._state_End(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: ContextDataTestCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Start" => ContextDataTestStateContext::Start,
    "End" => ContextDataTestStateContext::End,
    _ => ContextDataTestStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = ContextDataTestFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    ContextDataTestStateContext::Start => {}
    ContextDataTestStateContext::End => {}
    ContextDataTestStateContext::Empty => {}
}
    }

    pub fn process_with_data(&mut self, value: i32) -> String {
let __e = ContextDataTestFrameEvent::new("process_with_data");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_process_with_data(&__e, value),
            _ => Default::default(),
        }
    }

    pub fn check_data_isolation(&mut self) -> String {
let __e = ContextDataTestFrameEvent::new("check_data_isolation");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_check_data_isolation(&__e),
            _ => Default::default(),
        }
    }

    pub fn transition_preserves_data(&mut self, x: i32) -> String {
let __e = ContextDataTestFrameEvent::new("transition_preserves_data");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_transition_preserves_data(&__e, x),
            _ => Default::default(),
        }
    }

    fn _state_End(&mut self, __e: &ContextDataTestFrameEvent) {
match __e.message.as_str() {
    "$>" => { self._s_End_enter(__e); }
    _ => {}
}
    }

    fn _state_Start(&mut self, __e: &ContextDataTestFrameEvent) {
match __e.message.as_str() {
    "<$" => { self._s_Start_exit(__e); }
    "check_data_isolation" => { self._s_Start_check_data_isolation(__e); }
    _ => {}
}
    }

    fn _s_End_enter(&mut self, __e: &ContextDataTestFrameEvent) {
// Enter handler can access data set by previous handlers
/* @@:data["ended_in"] - context data not implemented for Rust */ = "End".to_string();

// Build final result from accumulated data
return format!(;
    "from={},to={},value={},exit_seen={}",
    /* @@:data["started_in"] - context data not implemented for Rust */,
    /* @@:data["ended_in"] - context data not implemented for Rust */,
    /* @@:data["value"] - context data not implemented for Rust */,
    /* @@:data["exit_seen"] - context data not implemented for Rust */
);
    }

    fn _s_Start_process_with_data(&mut self, __e: &ContextDataTestFrameEvent, value: i32) -> String {
// Set data in handler
/* @@:data["input"] - context data not implemented for Rust */ = /* @@.value - context params not implemented for Rust */.to_string();
return format!("processed:{}", /* @@:data[input] */);
    }

    fn _s_Start_transition_preserves_data(&mut self, __e: &ContextDataTestFrameEvent, x: i32) -> String {
// Set data, transition, verify data available in lifecycle handlers
/* @@:data["started_in"] - context data not implemented for Rust */ = "Start".to_string();
/* @@:data["value"] - context data not implemented for Rust */ = /* @@.x - context params not implemented for Rust */.to_string();
self.__transition(ContextDataTestCompartment::new("End"))
    }

    fn _s_Start_check_data_isolation(&mut self, __e: &ContextDataTestFrameEvent) -> String {
// Set data, call another method, verify our data preserved
/* @@:data["outer"] - context data not implemented for Rust */ = "outer_value".to_string();

// This creates its own context with its own data
let inner_result = self.process_with_data(99);

// Our data should still be here
return format!("outer_data={},inner={}", /* @@:data[outer] */, inner_result);
    }

    fn _s_Start_exit(&mut self, __e: &ContextDataTestFrameEvent) {
// Exit handler can access data set by event handler
/* @@:data["exit_seen"] - context data not implemented for Rust */ = "true".to_string();
    }
}


fn main() {
    println!("=== Test 38: Context Data ===");

    // Test 1: Basic data set/get
    let mut s1 = ContextDataTest::new();
    let result = s1.process_with_data(42);
    assert_eq!(result, "processed:42", "Expected 'processed:42', got '{}'", result);
    println!("1. process_with_data(42) = '{}'", result);

    // Test 2: Data isolation between nested calls
    let mut s2 = ContextDataTest::new();
    let result = s2.check_data_isolation();
    let expected = "outer_data=outer_value,inner=processed:99";
    assert_eq!(result, expected, "Expected '{}', got '{}'", expected, result);
    println!("2. check_data_isolation() = '{}'", result);

    // Test 3: Data preserved across transition (handler -> <$ -> $>)
    let mut s3 = ContextDataTest::new();
    let result = s3.transition_preserves_data(100);
    // Data should flow: handler sets -> exit accesses -> enter accesses and returns
    assert!(result.contains("from=Start"), "Expected 'from=Start' in '{}'", result);
    assert!(result.contains("to=End"), "Expected 'to=End' in '{}'", result);
    assert!(result.contains("value=100"), "Expected 'value=100' in '{}'", result);
    println!("3. transition_preserves_data(100) = '{}'", result);

    println!("PASS: Context data works correctly");
}
