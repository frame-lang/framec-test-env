use std::collections::HashMap;

#[derive(Clone, Debug)]
struct DomainVarsFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, String>,
}

impl DomainVarsFrameEvent {
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

struct DomainVarsFrameContext {
    event: DomainVarsFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl DomainVarsFrameContext {
    fn new(event: DomainVarsFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct DomainVarsCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<DomainVarsFrameEvent>,
}

impl DomainVarsCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum DomainVarsStateContext {
    Counting,
    Empty,
}

impl Default for DomainVarsStateContext {
    fn default() -> Self {
        DomainVarsStateContext::Counting
    }
}

pub struct DomainVars {
    _state_stack: Vec<(String, DomainVarsStateContext)>,
    __compartment: DomainVarsCompartment,
    __next_compartment: Option<DomainVarsCompartment>,
    _context_stack: Vec<DomainVarsFrameContext>,
    count: i32,
    name: String,
}

impl DomainVars {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            count: 0,
            name: String::from("counter"),
            __compartment: DomainVarsCompartment::new("Counting"),
            __next_compartment: None,
        };
let __frame_event = DomainVarsFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: DomainVarsFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = DomainVarsFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = DomainVarsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = DomainVarsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &DomainVarsFrameEvent) {
match self.__compartment.state.as_str() {
    "Counting" => self._state_Counting(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: DomainVarsCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Counting" => DomainVarsStateContext::Counting,
    _ => DomainVarsStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = DomainVarsFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    DomainVarsStateContext::Counting => {}
    DomainVarsStateContext::Empty => {}
}
    }

    pub fn increment(&mut self) {
let __e = DomainVarsFrameEvent::new("increment");
self.__kernel(__e);
    }

    pub fn decrement(&mut self) {
let __e = DomainVarsFrameEvent::new("decrement");
self.__kernel(__e);
    }

    pub fn get_count(&mut self) -> i32 {
let __e = DomainVarsFrameEvent::new("get_count");
match self.__compartment.state.as_str() {
            "Counting" => self._s_Counting_get_count(&__e),
            _ => Default::default(),
        }
    }

    pub fn set_count(&mut self, value: i32) {
let __e = DomainVarsFrameEvent::new("set_count");
match self.__compartment.state.as_str() {
            "Counting" => { self._s_Counting_set_count(&__e, value); }
            _ => {}
        }
// Process any pending transitions (bypassed kernel)
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = DomainVarsFrameEvent::new("$<");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = DomainVarsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = DomainVarsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn _state_Counting(&mut self, __e: &DomainVarsFrameEvent) {
match __e.message.as_str() {
    "decrement" => { self._s_Counting_decrement(__e); }
    "get_count" => { self._s_Counting_get_count(__e); }
    "increment" => { self._s_Counting_increment(__e); }
    _ => {}
}
    }

    fn _s_Counting_set_count(&mut self, __e: &DomainVarsFrameEvent, value: i32) {
self.count = value;
println!("{}: set to {}", self.name, self.count);
    }

    fn _s_Counting_increment(&mut self, __e: &DomainVarsFrameEvent) {
self.count += 1;
println!("{}: incremented to {}", self.name, self.count);
    }

    fn _s_Counting_decrement(&mut self, __e: &DomainVarsFrameEvent) {
self.count -= 1;
println!("{}: decremented to {}", self.name, self.count);
    }

    fn _s_Counting_get_count(&mut self, __e: &DomainVarsFrameEvent) -> i32 {
self.count
    }
}


fn main() {
    println!("=== Test 06: Domain Variables ===");
    let mut s = DomainVars::new();

    // Initial value should be 0
    let count = s.get_count();
    assert_eq!(count, 0, "Expected initial count=0, got {}", count);
    println!("Initial count: {}", count);

    // Increment
    s.increment();
    let count = s.get_count();
    assert_eq!(count, 1, "Expected count=1, got {}", count);

    s.increment();
    let count = s.get_count();
    assert_eq!(count, 2, "Expected count=2, got {}", count);

    // Decrement
    s.decrement();
    let count = s.get_count();
    assert_eq!(count, 1, "Expected count=1, got {}", count);

    // Set directly
    s.set_count(100);
    let count = s.get_count();
    assert_eq!(count, 100, "Expected count=100, got {}", count);

    println!("Final count: {}", count);
    println!("PASS: Domain variables work correctly");
}
