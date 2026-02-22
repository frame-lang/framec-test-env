use std::collections::HashMap;

#[derive(Clone, Debug)]
struct WithTransitionFrameEvent {
    message: String,
}

impl WithTransitionFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
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
}

impl WithTransition {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
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
    let exit_event = WithTransitionFrameEvent::new("$<");
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
let __e = WithTransitionFrameEvent::new("next");
self.__kernel(__e);
    }

    pub fn get_state(&mut self) -> String {
let __e = WithTransitionFrameEvent::new("get_state");
match self.__compartment.state.as_str() {
            "First" => self._s_First_get_state(&__e),
            "Second" => self._s_Second_get_state(&__e),
            _ => Default::default(),
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

    fn _s_First_get_state(&mut self, __e: &WithTransitionFrameEvent) -> String {
"First".to_string()
    }

    fn _s_Second_get_state(&mut self, __e: &WithTransitionFrameEvent) -> String {
"Second".to_string()
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
