
// Documentation Example: History with push$/pop$ (History201)


use std::collections::HashMap;

#[derive(Clone, Debug)]
struct HistoryBasicFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, String>,
}

impl HistoryBasicFrameEvent {
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

struct HistoryBasicFrameContext {
    event: HistoryBasicFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl HistoryBasicFrameContext {
    fn new(event: HistoryBasicFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct HistoryBasicCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<HistoryBasicFrameEvent>,
}

impl HistoryBasicCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum HistoryBasicStateContext {
    A,
    B,
    C,
    Empty,
}

impl Default for HistoryBasicStateContext {
    fn default() -> Self {
        HistoryBasicStateContext::A
    }
}

pub struct HistoryBasic {
    _state_stack: Vec<(String, HistoryBasicStateContext)>,
    __compartment: HistoryBasicCompartment,
    __next_compartment: Option<HistoryBasicCompartment>,
    _context_stack: Vec<HistoryBasicFrameContext>,
}

impl HistoryBasic {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            __compartment: HistoryBasicCompartment::new("A"),
            __next_compartment: None,
        };
let __frame_event = HistoryBasicFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: HistoryBasicFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = HistoryBasicFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = HistoryBasicFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = HistoryBasicFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &HistoryBasicFrameEvent) {
match self.__compartment.state.as_str() {
    "A" => self._state_A(__e),
    "B" => self._state_B(__e),
    "C" => self._state_C(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: HistoryBasicCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "A" => HistoryBasicStateContext::A,
    "B" => HistoryBasicStateContext::B,
    "C" => HistoryBasicStateContext::C,
    _ => HistoryBasicStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = HistoryBasicFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    HistoryBasicStateContext::A => {}
    HistoryBasicStateContext::B => {}
    HistoryBasicStateContext::C => {}
    HistoryBasicStateContext::Empty => {}
}
    }

    pub fn goto_c_from_a(&mut self) {
let __e = HistoryBasicFrameEvent::new("goto_c_from_a");
self.__kernel(__e);
    }

    pub fn goto_c_from_b(&mut self) {
let __e = HistoryBasicFrameEvent::new("goto_c_from_b");
self.__kernel(__e);
    }

    pub fn goto_b(&mut self) {
let __e = HistoryBasicFrameEvent::new("goto_b");
self.__kernel(__e);
    }

    pub fn return_back(&mut self) {
let __e = HistoryBasicFrameEvent::new("return_back");
self.__kernel(__e);
    }

    pub fn get_state(&mut self) -> String {
let __e = HistoryBasicFrameEvent::new("get_state");
match self.__compartment.state.as_str() {
            "A" => self._s_A_get_state(&__e),
            "B" => self._s_B_get_state(&__e),
            "C" => self._s_C_get_state(&__e),
            _ => Default::default(),
        }
    }

    fn _state_A(&mut self, __e: &HistoryBasicFrameEvent) {
match __e.message.as_str() {
    "get_state" => { self._s_A_get_state(__e); }
    "goto_b" => { self._s_A_goto_b(__e); }
    "goto_c_from_a" => { self._s_A_goto_c_from_a(__e); }
    _ => {}
}
    }

    fn _state_C(&mut self, __e: &HistoryBasicFrameEvent) {
match __e.message.as_str() {
    "get_state" => { self._s_C_get_state(__e); }
    "return_back" => { self._s_C_return_back(__e); }
    _ => {}
}
    }

    fn _state_B(&mut self, __e: &HistoryBasicFrameEvent) {
match __e.message.as_str() {
    "get_state" => { self._s_B_get_state(__e); }
    "goto_c_from_b" => { self._s_B_goto_c_from_b(__e); }
    _ => {}
}
    }

    fn _s_A_goto_b(&mut self, __e: &HistoryBasicFrameEvent) {
self.__transition(HistoryBasicCompartment::new("B"));
    }

    fn _s_A_get_state(&mut self, __e: &HistoryBasicFrameEvent) -> String {
return String::from("A")
    }

    fn _s_A_goto_c_from_a(&mut self, __e: &HistoryBasicFrameEvent) {
self._state_stack_push();
self.__transition(HistoryBasicCompartment::new("C"));
    }

    fn _s_C_return_back(&mut self, __e: &HistoryBasicFrameEvent) {
self._state_stack_pop();
return;
    }

    fn _s_C_get_state(&mut self, __e: &HistoryBasicFrameEvent) -> String {
return String::from("C")
    }

    fn _s_B_get_state(&mut self, __e: &HistoryBasicFrameEvent) -> String {
return String::from("B")
    }

    fn _s_B_goto_c_from_b(&mut self, __e: &HistoryBasicFrameEvent) {
self._state_stack_push();
self.__transition(HistoryBasicCompartment::new("C"));
    }
}


fn main() {
    println!("=== Test 33: Doc History Basic ===");
    let mut h = HistoryBasic::new();

    // Start in A
    assert_eq!(h.get_state(), "A", "Expected 'A'");

    // Go to C from A (push A)
    h.goto_c_from_a();
    assert_eq!(h.get_state(), "C", "Expected 'C'");

    // Return back (pop to A)
    h.return_back();
    assert_eq!(h.get_state(), "A", "Expected 'A' after pop");

    // Now go to B
    h.goto_b();
    assert_eq!(h.get_state(), "B", "Expected 'B'");

    // Go to C from B (push B)
    h.goto_c_from_b();
    assert_eq!(h.get_state(), "C", "Expected 'C'");

    // Return back (pop to B)
    h.return_back();
    assert_eq!(h.get_state(), "B", "Expected 'B' after pop");

    println!("PASS: History push/pop works correctly");
}
