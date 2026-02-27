use std::collections::HashMap;

struct MinimalFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl Clone for MinimalFrameEvent {
    fn clone(&self) -> Self {
        Self {
            message: self.message.clone(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

impl MinimalFrameEvent {
    fn new(message: &str) -> Self {
        Self {
            message: message.to_string(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

struct MinimalFrameContext {
    event: MinimalFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl MinimalFrameContext {
    fn new(event: MinimalFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct MinimalCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<MinimalFrameEvent>,
}

impl MinimalCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum MinimalStateContext {
    Start,
    Empty,
}

impl Default for MinimalStateContext {
    fn default() -> Self {
        MinimalStateContext::Start
    }
}

pub struct Minimal {
    _state_stack: Vec<(String, MinimalStateContext)>,
    __compartment: MinimalCompartment,
    __next_compartment: Option<MinimalCompartment>,
    _context_stack: Vec<MinimalFrameContext>,
}

impl Minimal {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            __compartment: MinimalCompartment::new("Start"),
            __next_compartment: None,
        };
let __frame_event = MinimalFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: MinimalFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = MinimalFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = MinimalFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = MinimalFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &MinimalFrameEvent) {
match self.__compartment.state.as_str() {
    "Start" => self._state_Start(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: MinimalCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Start" => MinimalStateContext::Start,
    _ => MinimalStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = MinimalFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    MinimalStateContext::Start => {}
    MinimalStateContext::Empty => {}
}
    }

    pub fn is_alive(&mut self) -> bool {
let mut __e = MinimalFrameEvent::new("is_alive");
let __ctx = MinimalFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Start" => { self._s_Start_is_alive(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = MinimalFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = MinimalFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = MinimalFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<bool>().unwrap()
} else {
    Default::default()
}
    }

    fn _state_Start(&mut self, __e: &MinimalFrameEvent) {
match __e.message.as_str() {
    "is_alive" => { self._s_Start_is_alive(__e); }
    _ => {}
}
    }

    fn _s_Start_is_alive(&mut self, __e: &MinimalFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(true)); }
return;
    }
}


fn main() {
    println!("=== Test 01: Minimal System ===");
    let mut s = Minimal::new();

    // Test that system instantiates and responds
    let result = s.is_alive();
    assert_eq!(result, true, "Expected true, got {}", result);
    println!("is_alive() = {}", result);

    println!("PASS: Minimal system works correctly");
}
