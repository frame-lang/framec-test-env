
// Rust version: Enter args not yet supported in Rust backend
// This test validates basic transitions work in Rust


use std::collections::HashMap;

struct TransitionEnterArgsFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl Clone for TransitionEnterArgsFrameEvent {
    fn clone(&self) -> Self {
        Self {
            message: self.message.clone(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

impl TransitionEnterArgsFrameEvent {
    fn new(message: &str) -> Self {
        Self {
            message: message.to_string(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

struct TransitionEnterArgsFrameContext {
    event: TransitionEnterArgsFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl TransitionEnterArgsFrameContext {
    fn new(event: TransitionEnterArgsFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct TransitionEnterArgsCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<TransitionEnterArgsFrameEvent>,
}

impl TransitionEnterArgsCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum TransitionEnterArgsStateContext {
    Idle,
    Active,
    Empty,
}

impl Default for TransitionEnterArgsStateContext {
    fn default() -> Self {
        TransitionEnterArgsStateContext::Idle
    }
}

pub struct TransitionEnterArgs {
    _state_stack: Vec<(String, TransitionEnterArgsStateContext)>,
    __compartment: TransitionEnterArgsCompartment,
    __next_compartment: Option<TransitionEnterArgsCompartment>,
    _context_stack: Vec<TransitionEnterArgsFrameContext>,
    count: i32,
}

impl TransitionEnterArgs {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            count: 0,
            __compartment: TransitionEnterArgsCompartment::new("Idle"),
            __next_compartment: None,
        };
let __frame_event = TransitionEnterArgsFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: TransitionEnterArgsFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = TransitionEnterArgsFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = TransitionEnterArgsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = TransitionEnterArgsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &TransitionEnterArgsFrameEvent) {
match self.__compartment.state.as_str() {
    "Idle" => self._state_Idle(__e),
    "Active" => self._state_Active(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: TransitionEnterArgsCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Idle" => TransitionEnterArgsStateContext::Idle,
    "Active" => TransitionEnterArgsStateContext::Active,
    _ => TransitionEnterArgsStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = TransitionEnterArgsFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    TransitionEnterArgsStateContext::Idle => {}
    TransitionEnterArgsStateContext::Active => {}
    TransitionEnterArgsStateContext::Empty => {}
}
    }

    pub fn start(&mut self) {
let mut __e = TransitionEnterArgsFrameEvent::new("start");
let __ctx = TransitionEnterArgsFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Idle" => { self._s_Idle_start(&__e); }
            "Active" => { self._s_Active_start(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = TransitionEnterArgsFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = TransitionEnterArgsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = TransitionEnterArgsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
self._context_stack.pop();
    }

    pub fn get_count(&mut self) -> i32 {
let mut __e = TransitionEnterArgsFrameEvent::new("get_count");
let __ctx = TransitionEnterArgsFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Idle" => { self._s_Idle_get_count(&__e); }
            "Active" => { self._s_Active_get_count(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = TransitionEnterArgsFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = TransitionEnterArgsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = TransitionEnterArgsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<i32>().unwrap()
} else {
    Default::default()
}
    }

    fn _state_Active(&mut self, __e: &TransitionEnterArgsFrameEvent) {
match __e.message.as_str() {
    "$>" => { self._s_Active_enter(__e); }
    "get_count" => { self._s_Active_get_count(__e); }
    "start" => { self._s_Active_start(__e); }
    _ => {}
}
    }

    fn _state_Idle(&mut self, __e: &TransitionEnterArgsFrameEvent) {
match __e.message.as_str() {
    "get_count" => { self._s_Idle_get_count(__e); }
    "start" => { self._s_Idle_start(__e); }
    _ => {}
}
    }

    fn _s_Active_enter(&mut self, __e: &TransitionEnterArgsFrameEvent) {
self.count = self.count + 1;
    }

    fn _s_Active_start(&mut self, __e: &TransitionEnterArgsFrameEvent) {
self.count = self.count + 10;
    }

    fn _s_Active_get_count(&mut self, __e: &TransitionEnterArgsFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(self.count)); }
return;;
    }

    fn _s_Idle_get_count(&mut self, __e: &TransitionEnterArgsFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(self.count)); }
return;;
    }

    fn _s_Idle_start(&mut self, __e: &TransitionEnterArgsFrameEvent) {
self.count = 1;
self.__transition(TransitionEnterArgsCompartment::new("Active"));
    }
}


fn main() {
    println!("=== Test 17: Transition Enter Args ===");
    let mut s = TransitionEnterArgs::new();

    // Initial state is Idle
    let count = s.get_count();
    assert_eq!(count, 0, "Expected count=0, got {}", count);

    // Transition to Active - enter handler should increment
    s.start();
    let count = s.get_count();
    // count should be 1 (from start) + 1 (from enter) = 2
    assert_eq!(count, 2, "Expected count=2, got {}", count);

    println!("PASS: Transition enter args work correctly");
}
