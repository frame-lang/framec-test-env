
// Test: Interface method return_init
// Validates that interface methods can have default return values
// Syntax: method(): type = default_value


use std::collections::HashMap;

#[derive(Clone, Debug)]
struct ReturnInitTestFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, String>,
}

impl ReturnInitTestFrameEvent {
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

struct ReturnInitTestFrameContext {
    event: ReturnInitTestFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl ReturnInitTestFrameContext {
    fn new(event: ReturnInitTestFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct ReturnInitTestCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<ReturnInitTestFrameEvent>,
}

impl ReturnInitTestCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum ReturnInitTestStateContext {
    Start,
    Active,
    Empty,
}

impl Default for ReturnInitTestStateContext {
    fn default() -> Self {
        ReturnInitTestStateContext::Start
    }
}

pub struct ReturnInitTest {
    _state_stack: Vec<(String, ReturnInitTestStateContext)>,
    __compartment: ReturnInitTestCompartment,
    __next_compartment: Option<ReturnInitTestCompartment>,
    _context_stack: Vec<ReturnInitTestFrameContext>,
}

impl ReturnInitTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            __compartment: ReturnInitTestCompartment::new("Start"),
            __next_compartment: None,
        };
let __frame_event = ReturnInitTestFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: ReturnInitTestFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = ReturnInitTestFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = ReturnInitTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = ReturnInitTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &ReturnInitTestFrameEvent) {
match self.__compartment.state.as_str() {
    "Start" => self._state_Start(__e),
    "Active" => self._state_Active(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: ReturnInitTestCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Start" => ReturnInitTestStateContext::Start,
    "Active" => ReturnInitTestStateContext::Active,
    _ => ReturnInitTestStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = ReturnInitTestFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    ReturnInitTestStateContext::Start => {}
    ReturnInitTestStateContext::Active => {}
    ReturnInitTestStateContext::Empty => {}
}
    }

    pub fn get_status(&mut self) -> String {
let __e = ReturnInitTestFrameEvent::new("get_status");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_get_status(&__e),
            "Active" => self._s_Active_get_status(&__e),
            _ => Default::default(),
        }
    }

    pub fn get_count(&mut self) -> i32 {
let __e = ReturnInitTestFrameEvent::new("get_count");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_get_count(&__e),
            "Active" => self._s_Active_get_count(&__e),
            _ => Default::default(),
        }
    }

    pub fn get_flag(&mut self) -> bool {
let __e = ReturnInitTestFrameEvent::new("get_flag");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_get_flag(&__e),
            "Active" => self._s_Active_get_flag(&__e),
            _ => Default::default(),
        }
    }

    pub fn trigger(&mut self) {
let __e = ReturnInitTestFrameEvent::new("trigger");
self.__kernel(__e);
    }

    fn _state_Active(&mut self, __e: &ReturnInitTestFrameEvent) {
match __e.message.as_str() {
    "$>" => { self._s_Active_enter(__e); }
    "get_count" => { self._s_Active_get_count(__e); }
    "get_flag" => { self._s_Active_get_flag(__e); }
    "get_status" => { self._s_Active_get_status(__e); }
    "trigger" => { self._s_Active_trigger(__e); }
    _ => {}
}
    }

    fn _state_Start(&mut self, __e: &ReturnInitTestFrameEvent) {
match __e.message.as_str() {
    "$>" => { self._s_Start_enter(__e); }
    "get_count" => { self._s_Start_get_count(__e); }
    "get_flag" => { self._s_Start_get_flag(__e); }
    "get_status" => { self._s_Start_get_status(__e); }
    "trigger" => { self._s_Start_trigger(__e); }
    _ => {}
}
    }

    fn _s_Active_get_count(&mut self, __e: &ReturnInitTestFrameEvent) {
return 42;
    }

    fn _s_Active_trigger(&mut self, __e: &ReturnInitTestFrameEvent) {
self.__transition(ReturnInitTestCompartment::new("Start"));
    }

    fn _s_Active_get_flag(&mut self, __e: &ReturnInitTestFrameEvent) {
return true;
    }

    fn _s_Active_enter(&mut self, __e: &ReturnInitTestFrameEvent) {
// Active state enter (no-op);
    }

    fn _s_Active_get_status(&mut self, __e: &ReturnInitTestFrameEvent) {
return String::from("active");
    }

    fn _s_Start_enter(&mut self, __e: &ReturnInitTestFrameEvent) {
// Start state enter (no-op);
    }

    fn _s_Start_get_count(&mut self, __e: &ReturnInitTestFrameEvent) {
// Don't set return - should use default 0;
    }

    fn _s_Start_trigger(&mut self, __e: &ReturnInitTestFrameEvent) {
self.__transition(ReturnInitTestCompartment::new("Active"));
    }

    fn _s_Start_get_status(&mut self, __e: &ReturnInitTestFrameEvent) {
// Don't set return - should use default "unknown";
    }

    fn _s_Start_get_flag(&mut self, __e: &ReturnInitTestFrameEvent) {
// Don't set return - should use default false;
    }
}


fn main() {
    println!("TAP version 14");
    println!("1..6");

    let mut s = ReturnInitTest::new();

    // Test 1: Default string return
    if s.get_status() == "unknown" {
        println!("ok 1 - default string return is 'unknown'");
    } else {
        println!("not ok 1 - default string return is 'unknown' # got {}", s.get_status());
    }

    // Test 2: Default int return
    if s.get_count() == 0 {
        println!("ok 2 - default int return is 0");
    } else {
        println!("not ok 2 - default int return is 0 # got {}", s.get_count());
    }

    // Test 3: Default bool return
    if s.get_flag() == false {
        println!("ok 3 - default bool return is false");
    } else {
        println!("not ok 3 - default bool return is false # got {}", s.get_flag());
    }

    // Transition to Active state
    s.trigger();

    // Test 4: Explicit string return overrides default
    if s.get_status() == "active" {
        println!("ok 4 - explicit return overrides default string");
    } else {
        println!("not ok 4 - explicit return overrides default string # got {}", s.get_status());
    }

    // Test 5: Explicit int return overrides default
    if s.get_count() == 42 {
        println!("ok 5 - explicit return overrides default int");
    } else {
        println!("not ok 5 - explicit return overrides default int # got {}", s.get_count());
    }

    // Test 6: Explicit bool return overrides default
    if s.get_flag() == true {
        println!("ok 6 - explicit return overrides default bool");
    } else {
        println!("not ok 6 - explicit return overrides default bool # got {}", s.get_flag());
    }

    println!("# PASS - return_init provides default return values");
}
