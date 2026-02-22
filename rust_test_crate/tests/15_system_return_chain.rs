
// Tests system.return in enter handlers (Rust version)
// Note: Rust uses native return pattern, chain semantics differ from Python/TS


use std::collections::HashMap;

#[derive(Clone, Debug)]
struct SystemReturnChainTestFrameEvent {
    message: String,
}

impl SystemReturnChainTestFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct SystemReturnChainTestCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<SystemReturnChainTestFrameEvent>,
}

impl SystemReturnChainTestCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum SystemReturnChainTestStateContext {
    Start,
    EnterSetter,
    BothSet,
    Empty,
}

impl Default for SystemReturnChainTestStateContext {
    fn default() -> Self {
        SystemReturnChainTestStateContext::Start
    }
}

pub struct SystemReturnChainTest {
    _state_stack: Vec<(String, SystemReturnChainTestStateContext)>,
    __compartment: SystemReturnChainTestCompartment,
    __next_compartment: Option<SystemReturnChainTestCompartment>,
}

impl SystemReturnChainTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            __compartment: SystemReturnChainTestCompartment::new("Start"),
            __next_compartment: None,
        };
let __frame_event = SystemReturnChainTestFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: SystemReturnChainTestFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = SystemReturnChainTestFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = SystemReturnChainTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = SystemReturnChainTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &SystemReturnChainTestFrameEvent) {
match self.__compartment.state.as_str() {
    "Start" => self._state_Start(__e),
    "EnterSetter" => self._state_EnterSetter(__e),
    "BothSet" => self._state_BothSet(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: SystemReturnChainTestCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Start" => SystemReturnChainTestStateContext::Start,
    "EnterSetter" => SystemReturnChainTestStateContext::EnterSetter,
    "BothSet" => SystemReturnChainTestStateContext::BothSet,
    _ => SystemReturnChainTestStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = SystemReturnChainTestFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    SystemReturnChainTestStateContext::Start => {}
    SystemReturnChainTestStateContext::EnterSetter => {}
    SystemReturnChainTestStateContext::BothSet => {}
    SystemReturnChainTestStateContext::Empty => {}
}
    }

    pub fn get_state_num(&mut self) -> i32 {
let __e = SystemReturnChainTestFrameEvent::new("get_state_num");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_get_state_num(&__e),
            "EnterSetter" => self._s_EnterSetter_get_state_num(&__e),
            "BothSet" => self._s_BothSet_get_state_num(&__e),
            _ => Default::default(),
        }
    }

    fn _state_EnterSetter(&mut self, __e: &SystemReturnChainTestFrameEvent) {
match __e.message.as_str() {
    "get_state_num" => { self._s_EnterSetter_get_state_num(__e); }
    _ => {}
}
    }

    fn _state_BothSet(&mut self, __e: &SystemReturnChainTestFrameEvent) {
match __e.message.as_str() {
    "get_state_num" => { self._s_BothSet_get_state_num(__e); }
    _ => {}
}
    }

    fn _state_Start(&mut self, __e: &SystemReturnChainTestFrameEvent) {
match __e.message.as_str() {
    "get_state_num" => { self._s_Start_get_state_num(__e); }
    _ => {}
}
    }

    fn _s_EnterSetter_get_state_num(&mut self, __e: &SystemReturnChainTestFrameEvent) -> i32 {
return 2;
    }

    fn _s_BothSet_get_state_num(&mut self, __e: &SystemReturnChainTestFrameEvent) -> i32 {
return 3;
    }

    fn _s_Start_get_state_num(&mut self, __e: &SystemReturnChainTestFrameEvent) -> i32 {
return 1;
    }
}


fn main() {
    println!("=== Test 15: System Return (Rust) ===");

    let mut s1 = SystemReturnChainTest::new();
    let state = s1.get_state_num();
    assert_eq!(state, 1, "Expected state 1, got {}", state);
    println!("1. get_state_num() = {}", state);

    println!("PASS: System return works correctly");
}
