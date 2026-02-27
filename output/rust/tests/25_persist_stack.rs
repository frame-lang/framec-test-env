use std::collections::HashMap;

#[derive(Clone, Debug)]
struct PersistStackFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, String>,
}

impl PersistStackFrameEvent {
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

struct PersistStackFrameContext {
    event: PersistStackFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl PersistStackFrameContext {
    fn new(event: PersistStackFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct PersistStackCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<PersistStackFrameEvent>,
}

impl PersistStackCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum PersistStackStateContext {
    Start,
    Middle,
    End,
    Empty,
}

impl Default for PersistStackStateContext {
    fn default() -> Self {
        PersistStackStateContext::Start
    }
}

pub struct PersistStack {
    _state_stack: Vec<(String, PersistStackStateContext)>,
    __compartment: PersistStackCompartment,
    __next_compartment: Option<PersistStackCompartment>,
    _context_stack: Vec<PersistStackFrameContext>,
    depth: i32,
}

impl PersistStack {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            depth: 0,
            __compartment: PersistStackCompartment::new("Start"),
            __next_compartment: None,
        };
let __frame_event = PersistStackFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: PersistStackFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = PersistStackFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = PersistStackFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = PersistStackFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &PersistStackFrameEvent) {
match self.__compartment.state.as_str() {
    "Start" => self._state_Start(__e),
    "Middle" => self._state_Middle(__e),
    "End" => self._state_End(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: PersistStackCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Start" => PersistStackStateContext::Start,
    "Middle" => PersistStackStateContext::Middle,
    "End" => PersistStackStateContext::End,
    _ => PersistStackStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = PersistStackFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    PersistStackStateContext::Start => {}
    PersistStackStateContext::Middle => {}
    PersistStackStateContext::End => {}
    PersistStackStateContext::Empty => {}
}
    }

    pub fn push_and_go(&mut self) {
let __e = PersistStackFrameEvent::new("push_and_go");
self.__kernel(__e);
    }

    pub fn pop_back(&mut self) {
let __e = PersistStackFrameEvent::new("pop_back");
self.__kernel(__e);
    }

    pub fn get_state(&mut self) -> String {
let __e = PersistStackFrameEvent::new("get_state");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_get_state(&__e),
            "Middle" => self._s_Middle_get_state(&__e),
            "End" => self._s_End_get_state(&__e),
            _ => Default::default(),
        }
    }

    pub fn get_depth(&mut self) -> i32 {
let __e = PersistStackFrameEvent::new("get_depth");
match self.__compartment.state.as_str() {
            "Start" => self._s_Start_get_depth(&__e),
            "Middle" => self._s_Middle_get_depth(&__e),
            "End" => self._s_End_get_depth(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Middle(&mut self, __e: &PersistStackFrameEvent) {
match __e.message.as_str() {
    "get_depth" => { self._s_Middle_get_depth(__e); }
    "get_state" => { self._s_Middle_get_state(__e); }
    "pop_back" => { self._s_Middle_pop_back(__e); }
    "push_and_go" => { self._s_Middle_push_and_go(__e); }
    _ => {}
}
    }

    fn _state_Start(&mut self, __e: &PersistStackFrameEvent) {
match __e.message.as_str() {
    "get_depth" => { self._s_Start_get_depth(__e); }
    "get_state" => { self._s_Start_get_state(__e); }
    "pop_back" => { self._s_Start_pop_back(__e); }
    "push_and_go" => { self._s_Start_push_and_go(__e); }
    _ => {}
}
    }

    fn _state_End(&mut self, __e: &PersistStackFrameEvent) {
match __e.message.as_str() {
    "get_depth" => { self._s_End_get_depth(__e); }
    "get_state" => { self._s_End_get_state(__e); }
    "pop_back" => { self._s_End_pop_back(__e); }
    "push_and_go" => { self._s_End_push_and_go(__e); }
    _ => {}
}
    }

    fn _s_Middle_get_state(&mut self, __e: &PersistStackFrameEvent) -> String {
return String::from("middle");
    }

    fn _s_Middle_push_and_go(&mut self, __e: &PersistStackFrameEvent) {
self.depth = self.depth + 1;
self._state_stack_push();
self.__transition(PersistStackCompartment::new("End"));
    }

    fn _s_Middle_pop_back(&mut self, __e: &PersistStackFrameEvent) {
self.depth = self.depth - 1;
self._state_stack_pop();
return;
    }

    fn _s_Middle_get_depth(&mut self, __e: &PersistStackFrameEvent) -> i32 {
return self.depth;
    }

    fn _s_Start_push_and_go(&mut self, __e: &PersistStackFrameEvent) {
self.depth = self.depth + 1;
self._state_stack_push();
self.__transition(PersistStackCompartment::new("Middle"));
    }

    fn _s_Start_get_depth(&mut self, __e: &PersistStackFrameEvent) -> i32 {
return self.depth;
    }

    fn _s_Start_get_state(&mut self, __e: &PersistStackFrameEvent) -> String {
return String::from("start");
    }

    fn _s_Start_pop_back(&mut self, __e: &PersistStackFrameEvent) {
// nothing to pop;
    }

    fn _s_End_pop_back(&mut self, __e: &PersistStackFrameEvent) {
self.depth = self.depth - 1;
self._state_stack_pop();
return;
    }

    fn _s_End_get_depth(&mut self, __e: &PersistStackFrameEvent) -> i32 {
return self.depth;
    }

    fn _s_End_get_state(&mut self, __e: &PersistStackFrameEvent) -> String {
return String::from("end");
    }

    fn _s_End_push_and_go(&mut self, __e: &PersistStackFrameEvent) {
// can't go further;
    }

    pub fn save_state(&mut self) -> String {
let stack_states: Vec<&str> = self._state_stack.iter().map(|(s, _)| s.as_str()).collect();
serde_json::json!({
    "_state": self.__compartment.state,
    "_state_stack": stack_states,
    "depth": self.depth,
}).to_string()
    }

    pub fn restore_state(json: &str) -> PersistStack {
let data: serde_json::Value = serde_json::from_str(json).unwrap();
let stack: Vec<(String, PersistStackStateContext)> = data["_state_stack"].as_array()
    .map(|arr| arr.iter()
        .filter_map(|v| v.as_str().map(|s| (s.to_string(), PersistStackStateContext::Empty)))
        .collect())
    .unwrap_or_default();
let mut instance = PersistStack {
    _state_stack: stack,
    __compartment: PersistStackCompartment::new(data["_state"].as_str().unwrap()),
    __next_compartment: None,
    depth: serde_json::from_value(data["depth"].clone()).unwrap(),
};
instance
    }
}


fn main() {
    println!("=== Test 25: Persist Stack (Rust) ===");

    // Test 1: Build up a stack
    let mut s1 = PersistStack::new();
    assert_eq!(s1.get_state(), "start", "Expected start");

    s1.push_and_go();  // Start -> Middle (push Start)
    assert_eq!(s1.get_state(), "middle", "Expected middle");
    assert_eq!(s1.get_depth(), 1, "Expected depth 1");

    s1.push_and_go();  // Middle -> End (push Middle)
    assert_eq!(s1.get_state(), "end", "Expected end");
    assert_eq!(s1.get_depth(), 2, "Expected depth 2");

    println!("1. Built stack: state={}, depth={}", s1.get_state(), s1.get_depth());

    // Test 2: Save state (should include stack)
    let json = s1.save_state();
    println!("2. Saved JSON: {}", json);
    assert!(json.contains("End"), "Expected End state in JSON");
    assert!(json.contains("_state_stack"), "Expected _state_stack in JSON");

    // Test 3: Restore and verify stack works
    let mut s2 = PersistStack::restore_state(&json);
    assert_eq!(s2.get_state(), "end", "Restored: expected end");
    assert_eq!(s2.get_depth(), 2, "Restored: expected depth 2");
    println!("3. Restored: state={}, depth={}", s2.get_state(), s2.get_depth());

    // Test 4: Pop should work after restore
    s2.pop_back();  // End -> Middle (pop)
    assert_eq!(s2.get_state(), "middle", "After pop: expected middle");
    assert_eq!(s2.get_depth(), 1, "After pop: expected depth 1");
    println!("4. After pop: state={}, depth={}", s2.get_state(), s2.get_depth());

    // Test 5: Pop again
    s2.pop_back();  // Middle -> Start (pop)
    assert_eq!(s2.get_state(), "start", "After 2nd pop: expected start");
    assert_eq!(s2.get_depth(), 0, "After 2nd pop: expected depth 0");
    println!("5. After 2nd pop: state={}, depth={}", s2.get_state(), s2.get_depth());

    println!("PASS: Persist stack works correctly");
}
