
// Documentation Example: HSM with History (History203)
// Refactored common gotoC behavior into parent state $AB


use std::collections::HashMap;

struct HistoryHSMFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl Clone for HistoryHSMFrameEvent {
    fn clone(&self) -> Self {
        Self {
            message: self.message.clone(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

impl HistoryHSMFrameEvent {
    fn new(message: &str) -> Self {
        Self {
            message: message.to_string(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

struct HistoryHSMFrameContext {
    event: HistoryHSMFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl HistoryHSMFrameContext {
    fn new(event: HistoryHSMFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct HistoryHSMCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<HistoryHSMFrameEvent>,
}

impl HistoryHSMCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum HistoryHSMStateContext {
    Waiting,
    A,
    B,
    AB,
    C,
    Empty,
}

impl Default for HistoryHSMStateContext {
    fn default() -> Self {
        HistoryHSMStateContext::Waiting
    }
}

pub struct HistoryHSM {
    _state_stack: Vec<(String, HistoryHSMStateContext)>,
    __compartment: HistoryHSMCompartment,
    __next_compartment: Option<HistoryHSMCompartment>,
    _context_stack: Vec<HistoryHSMFrameContext>,
    log: Vec<String>,
}

impl HistoryHSM {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            log: Vec::new(),
            __compartment: HistoryHSMCompartment::new("Waiting"),
            __next_compartment: None,
        };
let __frame_event = HistoryHSMFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: HistoryHSMFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = HistoryHSMFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = HistoryHSMFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = HistoryHSMFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &HistoryHSMFrameEvent) {
match self.__compartment.state.as_str() {
    "Waiting" => self._state_Waiting(__e),
    "A" => self._state_A(__e),
    "B" => self._state_B(__e),
    "AB" => self._state_AB(__e),
    "C" => self._state_C(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: HistoryHSMCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Waiting" => HistoryHSMStateContext::Waiting,
    "A" => HistoryHSMStateContext::A,
    "B" => HistoryHSMStateContext::B,
    "AB" => HistoryHSMStateContext::AB,
    "C" => HistoryHSMStateContext::C,
    _ => HistoryHSMStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = HistoryHSMFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    HistoryHSMStateContext::Waiting => {}
    HistoryHSMStateContext::A => {}
    HistoryHSMStateContext::B => {}
    HistoryHSMStateContext::AB => {}
    HistoryHSMStateContext::C => {}
    HistoryHSMStateContext::Empty => {}
}
    }

    pub fn goto_a(&mut self) {
let mut __e = HistoryHSMFrameEvent::new("goto_a");
let __ctx = HistoryHSMFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Waiting" => { self._s_Waiting_goto_a(&__e); }
            "B" => { self._s_B_goto_a(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = HistoryHSMFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = HistoryHSMFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = HistoryHSMFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
self._context_stack.pop();
    }

    pub fn goto_b(&mut self) {
let mut __e = HistoryHSMFrameEvent::new("goto_b");
let __ctx = HistoryHSMFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Waiting" => { self._s_Waiting_goto_b(&__e); }
            "A" => { self._s_A_goto_b(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = HistoryHSMFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = HistoryHSMFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = HistoryHSMFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
self._context_stack.pop();
    }

    pub fn goto_c(&mut self) {
let mut __e = HistoryHSMFrameEvent::new("goto_c");
let __ctx = HistoryHSMFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "A" => { self._s_AB_goto_c(&__e); }
            "B" => { self._s_AB_goto_c(&__e); }
            "AB" => { self._s_AB_goto_c(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = HistoryHSMFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = HistoryHSMFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = HistoryHSMFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
self._context_stack.pop();
    }

    pub fn go_back(&mut self) {
let mut __e = HistoryHSMFrameEvent::new("go_back");
let __ctx = HistoryHSMFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "C" => { self._s_C_go_back(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = HistoryHSMFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = HistoryHSMFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = HistoryHSMFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
self._context_stack.pop();
    }

    pub fn get_state(&mut self) -> String {
let mut __e = HistoryHSMFrameEvent::new("get_state");
let __ctx = HistoryHSMFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Waiting" => { self._s_Waiting_get_state(&__e); }
            "A" => { self._s_A_get_state(&__e); }
            "B" => { self._s_B_get_state(&__e); }
            "C" => { self._s_C_get_state(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = HistoryHSMFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = HistoryHSMFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = HistoryHSMFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<String>().unwrap()
} else {
    Default::default()
}
    }

    pub fn get_log(&mut self) -> Vec<String> {
let mut __e = HistoryHSMFrameEvent::new("get_log");
let __ctx = HistoryHSMFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Waiting" => { self._s_Waiting_get_log(&__e); }
            "A" => { self._s_A_get_log(&__e); }
            "B" => { self._s_B_get_log(&__e); }
            "C" => { self._s_C_get_log(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = HistoryHSMFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = HistoryHSMFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = HistoryHSMFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<Vec<String>>().unwrap()
} else {
    Default::default()
}
    }

    fn _state_A(&mut self, __e: &HistoryHSMFrameEvent) {
match __e.message.as_str() {
    "$>" => { self._s_A_enter(__e); }
    "get_log" => { self._s_A_get_log(__e); }
    "get_state" => { self._s_A_get_state(__e); }
    "goto_b" => { self._s_A_goto_b(__e); }
    _ => self._state_AB(__e),
}
    }

    fn _state_Waiting(&mut self, __e: &HistoryHSMFrameEvent) {
match __e.message.as_str() {
    "$>" => { self._s_Waiting_enter(__e); }
    "get_log" => { self._s_Waiting_get_log(__e); }
    "get_state" => { self._s_Waiting_get_state(__e); }
    "goto_a" => { self._s_Waiting_goto_a(__e); }
    "goto_b" => { self._s_Waiting_goto_b(__e); }
    _ => {}
}
    }

    fn _state_AB(&mut self, __e: &HistoryHSMFrameEvent) {
match __e.message.as_str() {
    "goto_c" => { self._s_AB_goto_c(__e); }
    _ => {}
}
    }

    fn _state_C(&mut self, __e: &HistoryHSMFrameEvent) {
match __e.message.as_str() {
    "$>" => { self._s_C_enter(__e); }
    "get_log" => { self._s_C_get_log(__e); }
    "get_state" => { self._s_C_get_state(__e); }
    "go_back" => { self._s_C_go_back(__e); }
    _ => {}
}
    }

    fn _state_B(&mut self, __e: &HistoryHSMFrameEvent) {
match __e.message.as_str() {
    "$>" => { self._s_B_enter(__e); }
    "get_log" => { self._s_B_get_log(__e); }
    "get_state" => { self._s_B_get_state(__e); }
    "goto_a" => { self._s_B_goto_a(__e); }
    _ => self._state_AB(__e),
}
    }

    fn _s_A_get_state(&mut self, __e: &HistoryHSMFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(String::from("A"))); }
return;
    }

    fn _s_A_get_log(&mut self, __e: &HistoryHSMFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(self.log.clone())); }
return;
    }

    fn _s_A_goto_b(&mut self, __e: &HistoryHSMFrameEvent) {
self.log_msg(String::from("goto_b"));
self.__transition(HistoryHSMCompartment::new("B"));
    }

    fn _s_A_enter(&mut self, __e: &HistoryHSMFrameEvent) {
self.log_msg(String::from("In $A"));
    }

    fn _s_Waiting_goto_a(&mut self, __e: &HistoryHSMFrameEvent) {
self.log_msg(String::from("goto_a"));
self.__transition(HistoryHSMCompartment::new("A"));
    }

    fn _s_Waiting_goto_b(&mut self, __e: &HistoryHSMFrameEvent) {
self.log_msg(String::from("goto_b"));
self.__transition(HistoryHSMCompartment::new("B"));
    }

    fn _s_Waiting_get_state(&mut self, __e: &HistoryHSMFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(String::from("Waiting"))); }
return;
    }

    fn _s_Waiting_get_log(&mut self, __e: &HistoryHSMFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(self.log.clone())); }
return;
    }

    fn _s_Waiting_enter(&mut self, __e: &HistoryHSMFrameEvent) {
self.log_msg(String::from("In $Waiting"));
    }

    fn _s_AB_goto_c(&mut self, __e: &HistoryHSMFrameEvent) {
self.log_msg(String::from("goto_c in $AB"));
self._state_stack_push();
self.__transition(HistoryHSMCompartment::new("C"));
    }

    fn _s_C_enter(&mut self, __e: &HistoryHSMFrameEvent) {
self.log_msg(String::from("In $C"));
    }

    fn _s_C_get_log(&mut self, __e: &HistoryHSMFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(self.log.clone())); }
return;
    }

    fn _s_C_go_back(&mut self, __e: &HistoryHSMFrameEvent) {
self.log_msg(String::from("go_back"));
self._state_stack_pop();
return;
    }

    fn _s_C_get_state(&mut self, __e: &HistoryHSMFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(String::from("C"))); }
return;
    }

    fn _s_B_enter(&mut self, __e: &HistoryHSMFrameEvent) {
self.log_msg(String::from("In $B"));
    }

    fn _s_B_goto_a(&mut self, __e: &HistoryHSMFrameEvent) {
self.log_msg(String::from("goto_a"));
self.__transition(HistoryHSMCompartment::new("A"));
    }

    fn _s_B_get_log(&mut self, __e: &HistoryHSMFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(self.log.clone())); }
return;
    }

    fn _s_B_get_state(&mut self, __e: &HistoryHSMFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(String::from("B"))); }
return;
    }

    fn log_msg(&mut self, msg: String) {
            self.log.push(msg);
    }
}


fn main() {
    println!("=== Test 34: Doc History HSM ===");
    let mut h = HistoryHSM::new();

    // Start in Waiting
    assert_eq!(h.get_state(), "Waiting", "Expected 'Waiting'");

    // Go to A
    h.goto_a();
    assert_eq!(h.get_state(), "A", "Expected 'A'");

    // Go to C (using inherited goto_c from $AB)
    h.goto_c();
    assert_eq!(h.get_state(), "C", "Expected 'C'");

    // Go back (should pop to A)
    h.go_back();
    assert_eq!(h.get_state(), "A", "Expected 'A' after go_back");

    // Go to B
    h.goto_b();
    assert_eq!(h.get_state(), "B", "Expected 'B'");

    // Go to C (again using inherited goto_c)
    h.goto_c();
    assert_eq!(h.get_state(), "C", "Expected 'C'");

    // Go back (should pop to B)
    h.go_back();
    assert_eq!(h.get_state(), "B", "Expected 'B' after go_back");

    println!("Log: {:?}", h.get_log());
    println!("PASS: HSM with history works correctly");
}
