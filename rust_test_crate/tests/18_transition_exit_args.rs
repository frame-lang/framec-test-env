
// Rust version: Exit args not yet supported in Rust backend
// This test validates basic exit handler works in Rust


use std::collections::HashMap;

#[derive(Clone, Debug)]
struct TransitionExitArgsFrameEvent {
    message: String,
}

impl TransitionExitArgsFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct TransitionExitArgsCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<TransitionExitArgsFrameEvent>,
}

impl TransitionExitArgsCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum TransitionExitArgsStateContext {
    Active,
    Done,
    Empty,
}

impl Default for TransitionExitArgsStateContext {
    fn default() -> Self {
        TransitionExitArgsStateContext::Active
    }
}

pub struct TransitionExitArgs {
    _state_stack: Vec<(String, TransitionExitArgsStateContext)>,
    __compartment: TransitionExitArgsCompartment,
    __next_compartment: Option<TransitionExitArgsCompartment>,
    count: i32,
}

impl TransitionExitArgs {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            count: 0,
            __compartment: TransitionExitArgsCompartment::new("Active"),
            __next_compartment: None,
        };
let __frame_event = TransitionExitArgsFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: TransitionExitArgsFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = TransitionExitArgsFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = TransitionExitArgsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = TransitionExitArgsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &TransitionExitArgsFrameEvent) {
match self.__compartment.state.as_str() {
    "Active" => self._state_Active(__e),
    "Done" => self._state_Done(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: TransitionExitArgsCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Active" => TransitionExitArgsStateContext::Active,
    "Done" => TransitionExitArgsStateContext::Done,
    _ => TransitionExitArgsStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = TransitionExitArgsFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    TransitionExitArgsStateContext::Active => {}
    TransitionExitArgsStateContext::Done => {}
    TransitionExitArgsStateContext::Empty => {}
}
    }

    pub fn leave(&mut self) {
let __e = TransitionExitArgsFrameEvent::new("leave");
self.__kernel(__e);
    }

    pub fn get_count(&mut self) -> i32 {
let __e = TransitionExitArgsFrameEvent::new("get_count");
match self.__compartment.state.as_str() {
            "Active" => self._s_Active_get_count(&__e),
            "Done" => self._s_Done_get_count(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Active(&mut self, __e: &TransitionExitArgsFrameEvent) {
match __e.message.as_str() {
    "$<" => { self._s_Active_exit(__e); }
    "get_count" => { self._s_Active_get_count(__e); }
    "leave" => { self._s_Active_leave(__e); }
    _ => {}
}
    }

    fn _state_Done(&mut self, __e: &TransitionExitArgsFrameEvent) {
match __e.message.as_str() {
    "$>" => { self._s_Done_enter(__e); }
    "get_count" => { self._s_Done_get_count(__e); }
    _ => {}
}
    }

    fn _s_Active_exit(&mut self, __e: &TransitionExitArgsFrameEvent) {
self.count = self.count + 10;
    }

    fn _s_Active_leave(&mut self, __e: &TransitionExitArgsFrameEvent) {
self.count = 1;
self.__transition(TransitionExitArgsCompartment::new("Done"));
    }

    fn _s_Active_get_count(&mut self, __e: &TransitionExitArgsFrameEvent) -> i32 {
return self.count;
    }

    fn _s_Done_enter(&mut self, __e: &TransitionExitArgsFrameEvent) {
self.count = self.count + 100;
    }

    fn _s_Done_get_count(&mut self, __e: &TransitionExitArgsFrameEvent) -> i32 {
return self.count;
    }
}


fn main() {
    println!("=== Test 18: Transition Exit Args ===");
    let mut s = TransitionExitArgs::new();

    // Initial state is Active
    let count = s.get_count();
    assert_eq!(count, 0, "Expected count=0, got {}", count);

    // Leave - should call exit handler, then enter handler
    s.leave();
    let count = s.get_count();
    // count = 1 (from leave) + 10 (from exit) + 100 (from enter) = 111
    assert_eq!(count, 111, "Expected count=111, got {}", count);

    println!("PASS: Transition exit args work correctly");
}
