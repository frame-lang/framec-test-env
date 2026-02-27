use std::collections::HashMap;

struct HSMForwardFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl Clone for HSMForwardFrameEvent {
    fn clone(&self) -> Self {
        Self {
            message: self.message.clone(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

impl HSMForwardFrameEvent {
    fn new(message: &str) -> Self {
        Self {
            message: message.to_string(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

struct HSMForwardFrameContext {
    event: HSMForwardFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl HSMForwardFrameContext {
    fn new(event: HSMForwardFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct HSMForwardCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<HSMForwardFrameEvent>,
}

impl HSMForwardCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum HSMForwardStateContext {
    Child,
    Parent,
    Empty,
}

impl Default for HSMForwardStateContext {
    fn default() -> Self {
        HSMForwardStateContext::Child
    }
}

pub struct HSMForward {
    _state_stack: Vec<(String, HSMForwardStateContext)>,
    __compartment: HSMForwardCompartment,
    __next_compartment: Option<HSMForwardCompartment>,
    _context_stack: Vec<HSMForwardFrameContext>,
    log: Vec<String>,
}

impl HSMForward {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            log: Vec::new(),
            __compartment: HSMForwardCompartment::new("Child"),
            __next_compartment: None,
        };
let __frame_event = HSMForwardFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: HSMForwardFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = HSMForwardFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = HSMForwardFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = HSMForwardFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &HSMForwardFrameEvent) {
match self.__compartment.state.as_str() {
    "Child" => self._state_Child(__e),
    "Parent" => self._state_Parent(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: HSMForwardCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Child" => HSMForwardStateContext::Child,
    "Parent" => HSMForwardStateContext::Parent,
    _ => HSMForwardStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = HSMForwardFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    HSMForwardStateContext::Child => {}
    HSMForwardStateContext::Parent => {}
    HSMForwardStateContext::Empty => {}
}
    }

    pub fn event_a(&mut self) {
let mut __e = HSMForwardFrameEvent::new("event_a");
let __ctx = HSMForwardFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Child" => { self._s_Child_event_a(&__e); }
            "Parent" => { self._s_Parent_event_a(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = HSMForwardFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = HSMForwardFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = HSMForwardFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
self._context_stack.pop();
    }

    pub fn event_b(&mut self) {
let mut __e = HSMForwardFrameEvent::new("event_b");
let __ctx = HSMForwardFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Child" => { self._s_Child_event_b(&__e); }
            "Parent" => { self._s_Parent_event_b(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = HSMForwardFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = HSMForwardFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = HSMForwardFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
self._context_stack.pop();
    }

    pub fn get_log(&mut self) -> Vec<String> {
let mut __e = HSMForwardFrameEvent::new("get_log");
let __ctx = HSMForwardFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Child" => { self._s_Child_get_log(&__e); }
            "Parent" => { self._s_Parent_get_log(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = HSMForwardFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = HSMForwardFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = HSMForwardFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<Vec<String>>().unwrap()
} else {
    Default::default()
}
    }

    fn _state_Child(&mut self, __e: &HSMForwardFrameEvent) {
match __e.message.as_str() {
    "event_a" => { self._s_Child_event_a(__e); }
    "event_b" => { self._s_Child_event_b(__e); }
    "get_log" => { self._s_Child_get_log(__e); }
    _ => self._state_Parent(__e),
}
    }

    fn _state_Parent(&mut self, __e: &HSMForwardFrameEvent) {
match __e.message.as_str() {
    "event_a" => { self._s_Parent_event_a(__e); }
    "event_b" => { self._s_Parent_event_b(__e); }
    "get_log" => { self._s_Parent_get_log(__e); }
    _ => {}
}
    }

    fn _s_Child_event_b(&mut self, __e: &HSMForwardFrameEvent) {
self.log.push("Child:event_b_forward".to_string());
self._state_Parent(__e);
    }

    fn _s_Child_get_log(&mut self, __e: &HSMForwardFrameEvent) {
self.log.clone();
    }

    fn _s_Child_event_a(&mut self, __e: &HSMForwardFrameEvent) {
self.log.push("Child:event_a".to_string());
    }

    fn _s_Parent_event_b(&mut self, __e: &HSMForwardFrameEvent) {
self.log.push("Parent:event_b".to_string());
    }

    fn _s_Parent_get_log(&mut self, __e: &HSMForwardFrameEvent) {
self.log.clone();
    }

    fn _s_Parent_event_a(&mut self, __e: &HSMForwardFrameEvent) {
self.log.push("Parent:event_a".to_string());
    }
}


fn main() {
    println!("=== Test 08: HSM Forward ===");
    let mut s = HSMForward::new();

    // event_a should be handled by Child (no forward)
    s.event_a();
    let log = s.get_log();
    assert!(log.contains(&"Child:event_a".to_string()), "Expected 'Child:event_a' in log, got {:?}", log);
    println!("After event_a: {:?}", log);

    // event_b should forward to Parent
    s.event_b();
    let log = s.get_log();
    assert!(log.contains(&"Child:event_b_forward".to_string()), "Expected 'Child:event_b_forward' in log, got {:?}", log);
    assert!(log.contains(&"Parent:event_b".to_string()), "Expected 'Parent:event_b' in log (forwarded), got {:?}", log);
    println!("After event_b (forwarded): {:?}", log);

    println!("PASS: HSM forward works correctly");
}
