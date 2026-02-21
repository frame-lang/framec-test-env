use std::collections::HashMap;

#[derive(Clone, Debug)]
struct WithInterfaceFrameEvent {
    message: String,
}

impl WithInterfaceFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct WithInterfaceCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<WithInterfaceFrameEvent>,
}

impl WithInterfaceCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum WithInterfaceStateContext {
    Ready,
    Empty,
}

impl Default for WithInterfaceStateContext {
    fn default() -> Self {
        WithInterfaceStateContext::Ready
    }
}

pub struct WithInterface {
    _state_stack: Vec<(String, WithInterfaceStateContext)>,
    __compartment: WithInterfaceCompartment,
    __next_compartment: Option<WithInterfaceCompartment>,
    call_count: i32,
}

impl WithInterface {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            call_count: 0,
            __compartment: WithInterfaceCompartment::new("Ready"),
            __next_compartment: None,
        };
let __frame_event = WithInterfaceFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: WithInterfaceFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = WithInterfaceFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = WithInterfaceFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = WithInterfaceFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &WithInterfaceFrameEvent) {
match self.__compartment.state.as_str() {
    "Ready" => self._state_Ready(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: WithInterfaceCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Ready" => WithInterfaceStateContext::Ready,
    _ => WithInterfaceStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = WithInterfaceFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    WithInterfaceStateContext::Ready => {}
    WithInterfaceStateContext::Empty => {}
}
    }

    pub fn greet(&mut self, name: &str) -> String {
let __e = WithInterfaceFrameEvent::new("greet");
match self.__compartment.state.as_str() {
            "Ready" => self._s_Ready_greet(&__e, name),
            _ => Default::default(),
        }
    }

    pub fn get_count(&mut self) -> i32 {
let __e = WithInterfaceFrameEvent::new("get_count");
match self.__compartment.state.as_str() {
            "Ready" => self._s_Ready_get_count(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Ready(&mut self, __e: &WithInterfaceFrameEvent) {
match __e.message.as_str() {
    "get_count" => { self._s_Ready_get_count(__e); }
    _ => {}
}
    }

    fn _s_Ready_greet(&mut self, __e: &WithInterfaceFrameEvent, name: &str) -> String {
self.call_count += 1;
format!("Hello, {}!", name)
    }

    fn _s_Ready_get_count(&mut self, __e: &WithInterfaceFrameEvent) -> i32 {
self.call_count
    }
}


fn main() {
    println!("=== Test 02: Interface Methods ===");
    let mut s = WithInterface::new();

    // Test interface method with parameter and return
    let result = s.greet("World");
    assert_eq!(result, "Hello, World!", "Expected 'Hello, World!', got '{}'", result);
    println!("greet('World') = {}", result);

    // Test domain variable access through interface
    let count = s.get_count();
    assert_eq!(count, 1, "Expected count=1, got {}", count);
    println!("get_count() = {}", count);

    // Call again to verify state
    s.greet("Frame");
    let count2 = s.get_count();
    assert_eq!(count2, 2, "Expected count=2, got {}", count2);
    println!("After second call: get_count() = {}", count2);

    println!("PASS: Interface methods work correctly");
}
