
// Rust now preserves state variables across push/pop using typed compartment enum.
// See generate_rust_compartment_types() in system_codegen.rs


use std::collections::HashMap;

#[derive(Clone, Debug)]
struct StateVarPushPopFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, String>,
}

impl StateVarPushPopFrameEvent {
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

struct StateVarPushPopFrameContext {
    event: StateVarPushPopFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl StateVarPushPopFrameContext {
    fn new(event: StateVarPushPopFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct StateVarPushPopCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<StateVarPushPopFrameEvent>,
}

impl StateVarPushPopCompartment {
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

#[derive(Clone, Default)]
struct OtherContext {
    other_count: i32,
}

#[derive(Clone)]
enum StateVarPushPopStateContext {
    Counter(CounterContext),
    Other(OtherContext),
    Empty,
}

impl Default for StateVarPushPopStateContext {
    fn default() -> Self {
        StateVarPushPopStateContext::Counter(CounterContext::default())
    }
}

pub struct StateVarPushPop {
    _state_stack: Vec<(String, StateVarPushPopStateContext)>,
    __compartment: StateVarPushPopCompartment,
    __next_compartment: Option<StateVarPushPopCompartment>,
    _context_stack: Vec<StateVarPushPopFrameContext>,
    _sv_count: i32,
    _sv_other_count: i32,
}

impl StateVarPushPop {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            _sv_count: 0,
            _sv_other_count: 0,
            __compartment: StateVarPushPopCompartment::new("Counter"),
            __next_compartment: None,
        };
let __frame_event = StateVarPushPopFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: StateVarPushPopFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = StateVarPushPopFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = StateVarPushPopFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = StateVarPushPopFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &StateVarPushPopFrameEvent) {
match self.__compartment.state.as_str() {
    "Counter" => self._state_Counter(__e),
    "Other" => self._state_Other(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: StateVarPushPopCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Counter" => StateVarPushPopStateContext::Counter(CounterContext { count: self._sv_count }),
    "Other" => StateVarPushPopStateContext::Other(OtherContext { other_count: self._sv_other_count }),
    _ => StateVarPushPopStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = StateVarPushPopFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    StateVarPushPopStateContext::Counter(ctx) => {
        self._sv_count = ctx.count;
    }
    StateVarPushPopStateContext::Other(ctx) => {
        self._sv_other_count = ctx.other_count;
    }
    StateVarPushPopStateContext::Empty => {}
}
    }

    pub fn increment(&mut self) -> i32 {
let __e = StateVarPushPopFrameEvent::new("increment");
match self.__compartment.state.as_str() {
            "Counter" => self._s_Counter_increment(&__e),
            "Other" => self._s_Other_increment(&__e),
            _ => Default::default(),
        }
    }

    pub fn get_count(&mut self) -> i32 {
let __e = StateVarPushPopFrameEvent::new("get_count");
match self.__compartment.state.as_str() {
            "Counter" => self._s_Counter_get_count(&__e),
            "Other" => self._s_Other_get_count(&__e),
            _ => Default::default(),
        }
    }

    pub fn save_and_go(&mut self) {
let __e = StateVarPushPopFrameEvent::new("save_and_go");
self.__kernel(__e);
    }

    pub fn restore(&mut self) {
let __e = StateVarPushPopFrameEvent::new("restore");
self.__kernel(__e);
    }

    fn _state_Counter(&mut self, __e: &StateVarPushPopFrameEvent) {
match __e.message.as_str() {
    "get_count" => { self._s_Counter_get_count(__e); }
    "increment" => { self._s_Counter_increment(__e); }
    "save_and_go" => { self._s_Counter_save_and_go(__e); }
    "$>" => {
        self._sv_count = 0;
    }
    _ => {}
}
    }

    fn _state_Other(&mut self, __e: &StateVarPushPopFrameEvent) {
match __e.message.as_str() {
    "get_count" => { self._s_Other_get_count(__e); }
    "increment" => { self._s_Other_increment(__e); }
    "restore" => { self._s_Other_restore(__e); }
    "$>" => {
        self._sv_other_count = 100;
    }
    _ => {}
}
    }

    fn _s_Counter_save_and_go(&mut self, __e: &StateVarPushPopFrameEvent) {
self._state_stack_push();
self.__transition(StateVarPushPopCompartment::new("Other"));
    }

    fn _s_Counter_get_count(&mut self, __e: &StateVarPushPopFrameEvent) -> i32 {
self._sv_count
    }

    fn _s_Counter_increment(&mut self, __e: &StateVarPushPopFrameEvent) -> i32 {
self._sv_count = self._sv_count + 1;
self._sv_count
    }

    fn _s_Other_get_count(&mut self, __e: &StateVarPushPopFrameEvent) -> i32 {
self._sv_other_count
    }

    fn _s_Other_restore(&mut self, __e: &StateVarPushPopFrameEvent) {
self._state_stack_pop();
return;
    }

    fn _s_Other_increment(&mut self, __e: &StateVarPushPopFrameEvent) -> i32 {
self._sv_other_count = self._sv_other_count + 1;
self._sv_other_count
    }
}


fn main() {
    println!("=== Test 12: State Variable Push/Pop ===");
    let mut s = StateVarPushPop::new();

    // Increment counter to 3
    s.increment();
    s.increment();
    s.increment();
    let count = s.get_count();
    assert_eq!(count, 3, "Expected 3, got {}", count);
    println!("Counter before push: {}", count);

    // Push and go to Other state
    s.save_and_go();
    println!("Pushed and transitioned to Other");

    // In Other state, count should be 100 (Other's state var)
    let count = s.get_count();
    assert_eq!(count, 100, "Expected 100 in Other state, got {}", count);
    println!("Other state count: {}", count);

    // Increment in Other
    s.increment();
    let count = s.get_count();
    assert_eq!(count, 101, "Expected 101 after increment, got {}", count);
    println!("Other state after increment: {}", count);

    // Pop back - state vars are now preserved in Rust (same as Python/TypeScript)
    s.restore();
    println!("Popped back to Counter");

    let count = s.get_count();
    // State vars are preserved across push/pop
    assert_eq!(count, 3, "Expected 3 after pop (preserved), got {}", count);
    println!("Counter after pop: {} (preserved!)", count);

    // Increment to verify it works
    s.increment();
    let count = s.get_count();
    assert_eq!(count, 4, "Expected 4, got {}", count);
    println!("Counter after increment: {}", count);

    println!("PASS: State vars preserved across push/pop");
}
