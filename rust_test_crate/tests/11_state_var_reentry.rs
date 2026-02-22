use std::collections::HashMap;

#[derive(Clone, Debug)]
struct StateVarReentryFrameEvent {
    message: String,
}

impl StateVarReentryFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct StateVarReentryCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<StateVarReentryFrameEvent>,
}

impl StateVarReentryCompartment {
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
enum StateVarReentryStateContext {
    Counter(CounterContext),
    Other,
    Empty,
}

impl Default for StateVarReentryStateContext {
    fn default() -> Self {
        StateVarReentryStateContext::Counter(CounterContext::default())
    }
}

pub struct StateVarReentry {
    _state_stack: Vec<(String, StateVarReentryStateContext)>,
    __compartment: StateVarReentryCompartment,
    __next_compartment: Option<StateVarReentryCompartment>,
    _sv_count: i32,
}

impl StateVarReentry {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _sv_count: 0,
            __compartment: StateVarReentryCompartment::new("Counter"),
            __next_compartment: None,
        };
let __frame_event = StateVarReentryFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: StateVarReentryFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = StateVarReentryFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = StateVarReentryFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = StateVarReentryFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &StateVarReentryFrameEvent) {
match self.__compartment.state.as_str() {
    "Counter" => self._state_Counter(__e),
    "Other" => self._state_Other(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: StateVarReentryCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Counter" => StateVarReentryStateContext::Counter(CounterContext { count: self._sv_count }),
    "Other" => StateVarReentryStateContext::Other,
    _ => StateVarReentryStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = StateVarReentryFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    StateVarReentryStateContext::Counter(ctx) => {
        self._sv_count = ctx.count;
    }
    StateVarReentryStateContext::Other => {}
    StateVarReentryStateContext::Empty => {}
}
    }

    pub fn increment(&mut self) -> i32 {
let __e = StateVarReentryFrameEvent::new("increment");
match self.__compartment.state.as_str() {
            "Counter" => self._s_Counter_increment(&__e),
            "Other" => self._s_Other_increment(&__e),
            _ => Default::default(),
        }
    }

    pub fn get_count(&mut self) -> i32 {
let __e = StateVarReentryFrameEvent::new("get_count");
match self.__compartment.state.as_str() {
            "Counter" => self._s_Counter_get_count(&__e),
            "Other" => self._s_Other_get_count(&__e),
            _ => Default::default(),
        }
    }

    pub fn go_other(&mut self) {
let __e = StateVarReentryFrameEvent::new("go_other");
self.__kernel(__e);
    }

    pub fn come_back(&mut self) {
let __e = StateVarReentryFrameEvent::new("come_back");
self.__kernel(__e);
    }

    fn _state_Counter(&mut self, __e: &StateVarReentryFrameEvent) {
match __e.message.as_str() {
    "get_count" => { self._s_Counter_get_count(__e); }
    "go_other" => { self._s_Counter_go_other(__e); }
    "increment" => { self._s_Counter_increment(__e); }
    "$>" => {
        self._sv_count = 0;
    }
    _ => {}
}
    }

    fn _state_Other(&mut self, __e: &StateVarReentryFrameEvent) {
match __e.message.as_str() {
    "come_back" => { self._s_Other_come_back(__e); }
    "get_count" => { self._s_Other_get_count(__e); }
    "increment" => { self._s_Other_increment(__e); }
    _ => {}
}
    }

    fn _s_Counter_get_count(&mut self, __e: &StateVarReentryFrameEvent) -> i32 {
self._sv_count
    }

    fn _s_Counter_increment(&mut self, __e: &StateVarReentryFrameEvent) -> i32 {
self._sv_count = self._sv_count + 1;
self._sv_count
    }

    fn _s_Counter_go_other(&mut self, __e: &StateVarReentryFrameEvent) {
self.__transition(StateVarReentryCompartment::new("Other"));
    }

    fn _s_Other_come_back(&mut self, __e: &StateVarReentryFrameEvent) {
self.__transition(StateVarReentryCompartment::new("Counter"));
    }

    fn _s_Other_increment(&mut self, __e: &StateVarReentryFrameEvent) -> i32 {
-1
    }

    fn _s_Other_get_count(&mut self, __e: &StateVarReentryFrameEvent) -> i32 {
-1
    }
}


fn main() {
    println!("=== Test 11: State Variable Reentry ===");
    let mut s = StateVarReentry::new();

    // Increment a few times
    s.increment();
    s.increment();
    let count = s.get_count();
    assert_eq!(count, 2, "Expected 2 after two increments, got {}", count);
    println!("Count before leaving: {}", count);

    // Leave the state
    s.go_other();
    println!("Transitioned to Other state");

    // Come back - state var should be reinitialized to 0
    s.come_back();
    let count = s.get_count();
    assert_eq!(count, 0, "Expected 0 after re-entering Counter (state var reinit), got {}", count);
    println!("Count after re-entering Counter: {}", count);

    // Increment again to verify it works
    let result = s.increment();
    assert_eq!(result, 1, "Expected 1 after increment, got {}", result);
    println!("After increment: {}", result);

    println!("PASS: State variables reinitialize on state reentry");
}
