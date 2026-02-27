use std::collections::HashMap;

struct WithTransitionFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl Clone for WithTransitionFrameEvent {
    fn clone(&self) -> Self {
        Self {
            message: self.message.clone(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

impl WithTransitionFrameEvent {
    fn new(message: &str) -> Self {
        Self {
            message: message.to_string(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

struct WithTransitionFrameContext {
    event: WithTransitionFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl WithTransitionFrameContext {
    fn new(event: WithTransitionFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct WithTransitionCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<WithTransitionFrameEvent>,
}

impl WithTransitionCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum WithTransitionStateContext {
    First,
    Second,
    Empty,
}

impl Default for WithTransitionStateContext {
    fn default() -> Self {
        WithTransitionStateContext::First
    }
}

pub struct WithTransition {
    _state_stack: Vec<(String, WithTransitionStateContext)>,
    __compartment: WithTransitionCompartment,
    __next_compartment: Option<WithTransitionCompartment>,
    _context_stack: Vec<WithTransitionFrameContext>,
}

impl WithTransition {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            __compartment: WithTransitionCompartment::new("First"),
            __next_compartment: None,
        };
let __frame_event = WithTransitionFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: WithTransitionFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = WithTransitionFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = WithTransitionFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = WithTransitionFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &WithTransitionFrameEvent) {
match self.__compartment.state.as_str() {
    "First" => self._state_First(__e),
    "Second" => self._state_Second(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: WithTransitionCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "First" => WithTransitionStateContext::First,
    "Second" => WithTransitionStateContext::Second,
    _ => WithTransitionStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = WithTransitionFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    WithTransitionStateContext::First => {}
    WithTransitionStateContext::Second => {}
    WithTransitionStateContext::Empty => {}
}
    }

    pub fn next(&mut self) {
let mut __e = WithTransitionFrameEvent::new("next");
let __ctx = WithTransitionFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "First" => { self._s_First_next(&__e); }
            "Second" => { self._s_Second_next(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = WithTransitionFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = WithTransitionFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = WithTransitionFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
self._context_stack.pop();
    }

    pub fn get_state(&mut self) -> String {
let mut __e = WithTransitionFrameEvent::new("get_state");
let __ctx = WithTransitionFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "First" => { self._s_First_get_state(&__e); }
            "Second" => { self._s_Second_get_state(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = WithTransitionFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = WithTransitionFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = WithTransitionFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<String>().unwrap()
} else {
    Default::default()
}
    }

    fn _state_First(&mut self, __e: &WithTransitionFrameEvent) {
match __e.message.as_str() {
    "get_state" => { self._s_First_get_state(__e); }
    "next" => { self._s_First_next(__e); }
    _ => {}
}
    }

    fn _state_Second(&mut self, __e: &WithTransitionFrameEvent) {
match __e.message.as_str() {
    "get_state" => { self._s_Second_get_state(__e); }
    "next" => { self._s_Second_next(__e); }
    _ => {}
}
    }

    fn _s_First_next(&mut self, __e: &WithTransitionFrameEvent) {
println!("Transitioning: First -> Second");
self.__transition(WithTransitionCompartment::new("Second"));
    }

    fn _s_First_get_state(&mut self, __e: &WithTransitionFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new("First".to_string())); }
return;
    }

    fn _s_Second_get_state(&mut self, __e: &WithTransitionFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new("Second".to_string())); }
return;
    }

    fn _s_Second_next(&mut self, __e: &WithTransitionFrameEvent) {
println!("Transitioning: Second -> First");
self.__transition(WithTransitionCompartment::new("First"));
    }
}


fn main() {
    println!("=== Test 03: State Transitions ===");
    let mut s = WithTransition::new();

    // Initial state should be First
    let state = s.get_state();
    assert_eq!(state, "First", "Expected 'First', got '{}'", state);
    println!("Initial state: {}", state);

    // Transition to Second
    s.next();
    let state = s.get_state();
    assert_eq!(state, "Second", "Expected 'Second', got '{}'", state);
    println!("After first next(): {}", state);

    // Transition back to First
    s.next();
    let state = s.get_state();
    assert_eq!(state, "First", "Expected 'First', got '{}'", state);
    println!("After second next(): {}", state);

    println!("PASS: State transitions work correctly");
}
