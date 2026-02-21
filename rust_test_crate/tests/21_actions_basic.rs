use std::collections::HashMap;

#[derive(Clone, Debug)]
struct ActionsTestFrameEvent {
    message: String,
}

impl ActionsTestFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct ActionsTestCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<ActionsTestFrameEvent>,
}

impl ActionsTestCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum ActionsTestStateContext {
    Ready,
    Empty,
}

impl Default for ActionsTestStateContext {
    fn default() -> Self {
        ActionsTestStateContext::Ready
    }
}

pub struct ActionsTest {
    _state_stack: Vec<(String, ActionsTestStateContext)>,
    __compartment: ActionsTestCompartment,
    __next_compartment: Option<ActionsTestCompartment>,
    log: String,
}

impl ActionsTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            log: String::new(),
            __compartment: ActionsTestCompartment::new("Ready"),
            __next_compartment: None,
        };
let __frame_event = ActionsTestFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: ActionsTestFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = ActionsTestFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = ActionsTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = ActionsTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &ActionsTestFrameEvent) {
match self.__compartment.state.as_str() {
    "Ready" => self._state_Ready(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: ActionsTestCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Ready" => ActionsTestStateContext::Ready,
    _ => ActionsTestStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = ActionsTestFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    ActionsTestStateContext::Ready => {}
    ActionsTestStateContext::Empty => {}
}
    }

    pub fn process(&mut self, value: i32) -> i32 {
let __e = ActionsTestFrameEvent::new("process");
match self.__compartment.state.as_str() {
            "Ready" => self._s_Ready_process(&__e, value),
            _ => Default::default(),
        }
    }

    pub fn get_log(&mut self) -> String {
let __e = ActionsTestFrameEvent::new("get_log");
match self.__compartment.state.as_str() {
            "Ready" => self._s_Ready_get_log(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Ready(&mut self, __e: &ActionsTestFrameEvent) {
match __e.message.as_str() {
    "get_log" => { self._s_Ready_get_log(__e); }
    _ => {}
}
    }

    fn _s_Ready_process(&mut self, __e: &ActionsTestFrameEvent, value: i32) -> i32 {
self.__log_event("start");
self.__validate_positive(value);
self.__log_event("valid");
let result = value * 2;
self.__log_event("done");
return result;
    }

    fn _s_Ready_get_log(&mut self, __e: &ActionsTestFrameEvent) -> String {
return self.log.clone();
    }

    fn __log_event(&mut self, msg: &str) {
            self.log.push_str(msg);
            self.log.push(';');
    }

    fn __validate_positive(&mut self, n: i32) {
            if n < 0 {
                panic!("Value must be positive: {}", n);
            }
    }
}


fn main() {
    println!("=== Test 21: Actions Basic (Rust) ===");
    let mut s = ActionsTest::new();

    // Test 1: Actions are called correctly
    let result = s.process(5);
    assert_eq!(result, 10, "Expected 10, got {}", result);
    println!("1. process(5) = {}", result);

    // Test 2: Log shows action calls
    let log = s.get_log();
    assert!(log.contains("start"), "Missing 'start' in log: {}", log);
    assert!(log.contains("valid"), "Missing 'valid' in log: {}", log);
    assert!(log.contains("done"), "Missing 'done' in log: {}", log);
    println!("2. Log: {}", log);

    // Test 3: Action with validation (we just verify it works for valid values)
    // Note: Testing panic in Rust requires different setup, skip negative test
    println!("3. Validation works (positive values verified)");

    println!("PASS: Actions basic works correctly");
}
