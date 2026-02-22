use std::collections::HashMap;

#[derive(Clone, Debug)]
struct HSMDefaultForwardFrameEvent {
    message: String,
}

impl HSMDefaultForwardFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct HSMDefaultForwardCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<HSMDefaultForwardFrameEvent>,
}

impl HSMDefaultForwardCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum HSMDefaultForwardStateContext {
    Child,
    Parent,
    Empty,
}

impl Default for HSMDefaultForwardStateContext {
    fn default() -> Self {
        HSMDefaultForwardStateContext::Child
    }
}

pub struct HSMDefaultForward {
    _state_stack: Vec<(String, HSMDefaultForwardStateContext)>,
    __compartment: HSMDefaultForwardCompartment,
    __next_compartment: Option<HSMDefaultForwardCompartment>,
    log: Vec<String>,
}

impl HSMDefaultForward {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            log: Vec::new(),
            __compartment: HSMDefaultForwardCompartment::new("Child"),
            __next_compartment: None,
        };
let __frame_event = HSMDefaultForwardFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: HSMDefaultForwardFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = HSMDefaultForwardFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = HSMDefaultForwardFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = HSMDefaultForwardFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &HSMDefaultForwardFrameEvent) {
match self.__compartment.state.as_str() {
    "Child" => self._state_Child(__e),
    "Parent" => self._state_Parent(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: HSMDefaultForwardCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Child" => HSMDefaultForwardStateContext::Child,
    "Parent" => HSMDefaultForwardStateContext::Parent,
    _ => HSMDefaultForwardStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = HSMDefaultForwardFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    HSMDefaultForwardStateContext::Child => {}
    HSMDefaultForwardStateContext::Parent => {}
    HSMDefaultForwardStateContext::Empty => {}
}
    }

    pub fn handled_event(&mut self) {
let __e = HSMDefaultForwardFrameEvent::new("handled_event");
self.__kernel(__e);
    }

    pub fn unhandled_event(&mut self) {
let __e = HSMDefaultForwardFrameEvent::new("unhandled_event");
self.__kernel(__e);
    }

    pub fn get_log(&mut self) -> Vec<String> {
let __e = HSMDefaultForwardFrameEvent::new("get_log");
match self.__compartment.state.as_str() {
            "Child" => self._s_Child_get_log(&__e),
            "Parent" => self._s_Parent_get_log(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Parent(&mut self, __e: &HSMDefaultForwardFrameEvent) {
match __e.message.as_str() {
    "get_log" => { self._s_Parent_get_log(__e); }
    "handled_event" => { self._s_Parent_handled_event(__e); }
    "unhandled_event" => { self._s_Parent_unhandled_event(__e); }
    _ => {}
}
    }

    fn _state_Child(&mut self, __e: &HSMDefaultForwardFrameEvent) {
match __e.message.as_str() {
    "get_log" => { self._s_Child_get_log(__e); }
    "handled_event" => { self._s_Child_handled_event(__e); }
    _ => self._state_Parent(__e),
}
    }

    fn _s_Parent_handled_event(&mut self, __e: &HSMDefaultForwardFrameEvent) {
self.log.push("Parent:handled_event".to_string());
    }

    fn _s_Parent_get_log(&mut self, __e: &HSMDefaultForwardFrameEvent) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Parent_unhandled_event(&mut self, __e: &HSMDefaultForwardFrameEvent) {
self.log.push("Parent:unhandled_event".to_string());
    }

    fn _s_Child_handled_event(&mut self, __e: &HSMDefaultForwardFrameEvent) {
self.log.push("Child:handled_event".to_string());
    }

    fn _s_Child_get_log(&mut self, __e: &HSMDefaultForwardFrameEvent) -> Vec<String> {
return self.log.clone();
    }
}


fn main() {
    println!("=== Test 30: HSM State-Level Default Forward (Rust) ===");
    let mut s = HSMDefaultForward::new();

    s.handled_event();
    let log = s.get_log();
    assert!(log.contains(&"Child:handled_event".to_string()),
            "Expected 'Child:handled_event' in log, got {:?}", log);
    println!("After handled_event: {:?}", log);

    s.unhandled_event();
    let log = s.get_log();
    assert!(log.contains(&"Parent:unhandled_event".to_string()),
            "Expected 'Parent:unhandled_event' in log (forwarded), got {:?}", log);
    println!("After unhandled_event (forwarded): {:?}", log);

    println!("PASS: HSM state-level default forward works correctly");
}
