use std::collections::HashMap;

#[derive(Clone, Debug)]
struct EventForwardTestFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, String>,
}

impl EventForwardTestFrameEvent {
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

struct EventForwardTestFrameContext {
    event: EventForwardTestFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl EventForwardTestFrameContext {
    fn new(event: EventForwardTestFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct EventForwardTestCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<EventForwardTestFrameEvent>,
}

impl EventForwardTestCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum EventForwardTestStateContext {
    Idle,
    Working,
    Empty,
}

impl Default for EventForwardTestStateContext {
    fn default() -> Self {
        EventForwardTestStateContext::Idle
    }
}

pub struct EventForwardTest {
    _state_stack: Vec<(String, EventForwardTestStateContext)>,
    __compartment: EventForwardTestCompartment,
    __next_compartment: Option<EventForwardTestCompartment>,
    _context_stack: Vec<EventForwardTestFrameContext>,
    log: Vec<String>,
}

impl EventForwardTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            log: Vec::new(),
            __compartment: EventForwardTestCompartment::new("Idle"),
            __next_compartment: None,
        };
let __frame_event = EventForwardTestFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: EventForwardTestFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = EventForwardTestFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = EventForwardTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = EventForwardTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &EventForwardTestFrameEvent) {
match self.__compartment.state.as_str() {
    "Idle" => self._state_Idle(__e),
    "Working" => self._state_Working(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: EventForwardTestCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Idle" => EventForwardTestStateContext::Idle,
    "Working" => EventForwardTestStateContext::Working,
    _ => EventForwardTestStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = EventForwardTestFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    EventForwardTestStateContext::Idle => {}
    EventForwardTestStateContext::Working => {}
    EventForwardTestStateContext::Empty => {}
}
    }

    pub fn process(&mut self) {
let __e = EventForwardTestFrameEvent::new("process");
self.__kernel(__e);
    }

    pub fn get_log(&mut self) -> Vec<String> {
let __e = EventForwardTestFrameEvent::new("get_log");
match self.__compartment.state.as_str() {
            "Idle" => self._s_Idle_get_log(&__e),
            "Working" => self._s_Working_get_log(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Working(&mut self, __e: &EventForwardTestFrameEvent) {
match __e.message.as_str() {
    "get_log" => { self._s_Working_get_log(__e); }
    "process" => { self._s_Working_process(__e); }
    _ => {}
}
    }

    fn _state_Idle(&mut self, __e: &EventForwardTestFrameEvent) {
match __e.message.as_str() {
    "get_log" => { self._s_Idle_get_log(__e); }
    "process" => { self._s_Idle_process(__e); }
    _ => {}
}
    }

    fn _s_Working_process(&mut self, __e: &EventForwardTestFrameEvent) {
self.log.push("working:process".to_string());
    }

    fn _s_Working_get_log(&mut self, __e: &EventForwardTestFrameEvent) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Idle_get_log(&mut self, __e: &EventForwardTestFrameEvent) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Idle_process(&mut self, __e: &EventForwardTestFrameEvent) {
self.log.push("idle:process:before".to_string());
let mut __compartment = EventForwardTestCompartment::new("Working");
__compartment.forward_event = Some(__e.clone());
self.__transition(__compartment);
return;
// This should NOT execute because -> => returns after dispatch
self.log.push("idle:process:after".to_string());
    }
}


fn main() {
    println!("=== Test 19: Transition Forward (Rust) ===");
    let mut s = EventForwardTest::new();
    s.process();
    let log = s.get_log();
    println!("Log: {:?}", log);

    // After transition-forward:
    // - Idle logs "idle:process:before"
    // - Transition to Working
    // - Working handles process(), logs "working:process"
    // - Return prevents "idle:process:after"
    assert!(log.contains(&"idle:process:before".to_string()), "Expected 'idle:process:before' in log: {:?}", log);
    assert!(log.contains(&"working:process".to_string()), "Expected 'working:process' in log: {:?}", log);
    assert!(!log.contains(&"idle:process:after".to_string()), "Should NOT have 'idle:process:after' in log: {:?}", log);

    println!("PASS: Transition forward works correctly");
}
