use std::collections::HashMap;

#[derive(Clone, Debug)]
struct WithParamsFrameEvent {
    message: String,
}

impl WithParamsFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct WithParamsCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<WithParamsFrameEvent>,
}

impl WithParamsCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum WithParamsStateContext {
    Idle,
    Running,
    Empty,
}

impl Default for WithParamsStateContext {
    fn default() -> Self {
        WithParamsStateContext::Idle
    }
}

pub struct WithParams {
    _state_stack: Vec<(String, WithParamsStateContext)>,
    __compartment: WithParamsCompartment,
    __next_compartment: Option<WithParamsCompartment>,
    total: i32,
}

impl WithParams {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            total: 0,
            __compartment: WithParamsCompartment::new("Idle"),
            __next_compartment: None,
        };
let __frame_event = WithParamsFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: WithParamsFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = WithParamsFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = WithParamsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = WithParamsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &WithParamsFrameEvent) {
match self.__compartment.state.as_str() {
    "Idle" => self._state_Idle(__e),
    "Running" => self._state_Running(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: WithParamsCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Idle" => WithParamsStateContext::Idle,
    "Running" => WithParamsStateContext::Running,
    _ => WithParamsStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = WithParamsFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    WithParamsStateContext::Idle => {}
    WithParamsStateContext::Running => {}
    WithParamsStateContext::Empty => {}
}
    }

    pub fn start(&mut self, initial: i32) {
let __e = WithParamsFrameEvent::new("start");
match self.__compartment.state.as_str() {
            "Idle" => { self._s_Idle_start(&__e, initial); }
            "Running" => { self._s_Running_start(&__e, initial); }
            _ => {}
        }
// Process any pending transitions (bypassed kernel)
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = WithParamsFrameEvent::new("$<");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = WithParamsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = WithParamsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    pub fn add(&mut self, value: i32) {
let __e = WithParamsFrameEvent::new("add");
match self.__compartment.state.as_str() {
            "Idle" => { self._s_Idle_add(&__e, value); }
            "Running" => { self._s_Running_add(&__e, value); }
            _ => {}
        }
// Process any pending transitions (bypassed kernel)
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = WithParamsFrameEvent::new("$<");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = WithParamsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = WithParamsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    pub fn multiply(&mut self, a: i32, b: i32) -> i32 {
let __e = WithParamsFrameEvent::new("multiply");
match self.__compartment.state.as_str() {
            "Idle" => self._s_Idle_multiply(&__e, a, b),
            "Running" => self._s_Running_multiply(&__e, a, b),
            _ => Default::default(),
        }
    }

    pub fn get_total(&mut self) -> i32 {
let __e = WithParamsFrameEvent::new("get_total");
match self.__compartment.state.as_str() {
            "Idle" => self._s_Idle_get_total(&__e),
            "Running" => self._s_Running_get_total(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Running(&mut self, __e: &WithParamsFrameEvent) {
match __e.message.as_str() {
    "get_total" => { self._s_Running_get_total(__e); }
    _ => {}
}
    }

    fn _state_Idle(&mut self, __e: &WithParamsFrameEvent) {
match __e.message.as_str() {
    "get_total" => { self._s_Idle_get_total(__e); }
    _ => {}
}
    }

    fn _s_Running_start(&mut self, __e: &WithParamsFrameEvent, initial: i32) {
println!("Already running");
    }

    fn _s_Running_add(&mut self, __e: &WithParamsFrameEvent, value: i32) {
self.total += value;
println!("Added {}, total is now {}", value, self.total);
    }

    fn _s_Running_get_total(&mut self, __e: &WithParamsFrameEvent) -> i32 {
self.total
    }

    fn _s_Running_multiply(&mut self, __e: &WithParamsFrameEvent, a: i32, b: i32) -> i32 {
let result = a * b;
self.total += result;
println!("Multiplied {} * {} = {}, total is now {}", a, b, result, self.total);
result
    }

    fn _s_Idle_start(&mut self, __e: &WithParamsFrameEvent, initial: i32) {
self.total = initial;
println!("Started with initial value: {}", initial);
self.__transition(WithParamsCompartment::new("Running"));
    }

    fn _s_Idle_add(&mut self, __e: &WithParamsFrameEvent, value: i32) {
println!("Cannot add in Idle state");
    }

    fn _s_Idle_multiply(&mut self, __e: &WithParamsFrameEvent, a: i32, b: i32) -> i32 {
0
    }

    fn _s_Idle_get_total(&mut self, __e: &WithParamsFrameEvent) -> i32 {
self.total
    }
}


fn main() {
    println!("=== Test 07: Handler Parameters ===");
    let mut s = WithParams::new();

    // Initial total should be 0
    let total = s.get_total();
    assert_eq!(total, 0, "Expected initial total=0, got {}", total);

    // Start with initial value
    s.start(100);
    let total = s.get_total();
    assert_eq!(total, 100, "Expected total=100, got {}", total);
    println!("After start(100): total = {}", total);

    // Add value
    s.add(25);
    let total = s.get_total();
    assert_eq!(total, 125, "Expected total=125, got {}", total);
    println!("After add(25): total = {}", total);

    // Multiply with two params
    let result = s.multiply(3, 5);
    assert_eq!(result, 15, "Expected multiply result=15, got {}", result);
    let total = s.get_total();
    assert_eq!(total, 140, "Expected total=140, got {}", total);
    println!("After multiply(3,5): result = {}, total = {}", result, total);

    println!("PASS: Handler parameters work correctly");
}
