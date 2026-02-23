use std::collections::HashMap;

#[derive(Clone, Debug)]
struct StateVarBasicFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, String>,
}

impl StateVarBasicFrameEvent {
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

struct StateVarBasicFrameContext {
    event: StateVarBasicFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl StateVarBasicFrameContext {
    fn new(event: StateVarBasicFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct StateVarBasicCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<StateVarBasicFrameEvent>,
}

impl StateVarBasicCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone, Default)]
struct CounterContext {
    count: i32,
}

#[derive(Clone)]
enum StateVarBasicStateContext {
    Counter(CounterContext),
    Empty,
}

impl Default for StateVarBasicStateContext {
    fn default() -> Self {
        StateVarBasicStateContext::Counter(CounterContext::default())
    }
}

pub struct StateVarBasic {
    _state_stack: Vec<(String, StateVarBasicStateContext)>,
    __compartment: StateVarBasicCompartment,
    __next_compartment: Option<StateVarBasicCompartment>,
    _context_stack: Vec<StateVarBasicFrameContext>,
    _sv_count: i32,
}

impl StateVarBasic {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            _sv_count: 0,
            __compartment: StateVarBasicCompartment::new("Counter"),
            __next_compartment: None,
        };
let __frame_event = StateVarBasicFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: StateVarBasicFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = StateVarBasicFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = StateVarBasicFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = StateVarBasicFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &StateVarBasicFrameEvent) {
match self.__compartment.state.as_str() {
    "Counter" => self._state_Counter(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: StateVarBasicCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Counter" => StateVarBasicStateContext::Counter(CounterContext { count: self._sv_count }),
    _ => StateVarBasicStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = StateVarBasicFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    StateVarBasicStateContext::Counter(ctx) => {
        self._sv_count = ctx.count;
    }
    StateVarBasicStateContext::Empty => {}
}
    }

    pub fn increment(&mut self) -> i32 {
let __e = StateVarBasicFrameEvent::new("increment");
match self.__compartment.state.as_str() {
            "Counter" => self._s_Counter_increment(&__e),
            _ => Default::default(),
        }
    }

    pub fn get_count(&mut self) -> i32 {
let __e = StateVarBasicFrameEvent::new("get_count");
match self.__compartment.state.as_str() {
            "Counter" => self._s_Counter_get_count(&__e),
            _ => Default::default(),
        }
    }

    pub fn reset(&mut self) {
let __e = StateVarBasicFrameEvent::new("reset");
self.__kernel(__e);
    }

    fn _state_Counter(&mut self, __e: &StateVarBasicFrameEvent) {
match __e.message.as_str() {
    "get_count" => { self._s_Counter_get_count(__e); }
    "increment" => { self._s_Counter_increment(__e); }
    "reset" => { self._s_Counter_reset(__e); }
    "$>" => {
        self._sv_count = 0;
    }
    _ => {}
}
    }

    fn _s_Counter_get_count(&mut self, __e: &StateVarBasicFrameEvent) -> i32 {
self._sv_count
    }

    fn _s_Counter_reset(&mut self, __e: &StateVarBasicFrameEvent) {
self._sv_count = 0;
    }

    fn _s_Counter_increment(&mut self, __e: &StateVarBasicFrameEvent) -> i32 {
self._sv_count = self._sv_count + 1;
self._sv_count
    }
}


fn main() {
    println!("=== Test 10: State Variable Basic ===");
    let mut s = StateVarBasic::new();

    // Initial value should be 0
    let count = s.get_count();
    assert_eq!(count, 0, "Expected 0, got {}", count);
    println!("Initial count: {}", count);

    // Increment should return new value
    let result = s.increment();
    assert_eq!(result, 1, "Expected 1 after first increment, got {}", result);
    println!("After first increment: {}", result);

    // Second increment
    let result = s.increment();
    assert_eq!(result, 2, "Expected 2 after second increment, got {}", result);
    println!("After second increment: {}", result);

    // Reset should set back to 0
    s.reset();
    let count = s.get_count();
    assert_eq!(count, 0, "Expected 0 after reset, got {}", count);
    println!("After reset: {}", count);

    println!("PASS: State variable basic operations work correctly");
}
