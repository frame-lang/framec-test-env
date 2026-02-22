use std::collections::HashMap;

#[derive(Clone, Debug)]
struct TransitionPopTestFrameEvent {
    message: String,
}

impl TransitionPopTestFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct TransitionPopTestCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<TransitionPopTestFrameEvent>,
}

impl TransitionPopTestCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum TransitionPopTestStateContext {
    Idle,
    Working,
    Empty,
}

impl Default for TransitionPopTestStateContext {
    fn default() -> Self {
        TransitionPopTestStateContext::Idle
    }
}

pub struct TransitionPopTest {
    _state_stack: Vec<(String, TransitionPopTestStateContext)>,
    __compartment: TransitionPopTestCompartment,
    __next_compartment: Option<TransitionPopTestCompartment>,
    log: Vec<String>,
}

impl TransitionPopTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            log: Vec::new(),
            __compartment: TransitionPopTestCompartment::new("Idle"),
            __next_compartment: None,
        };
let __frame_event = TransitionPopTestFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: TransitionPopTestFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = TransitionPopTestFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = TransitionPopTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = TransitionPopTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &TransitionPopTestFrameEvent) {
match self.__compartment.state.as_str() {
    "Idle" => self._state_Idle(__e),
    "Working" => self._state_Working(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: TransitionPopTestCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Idle" => TransitionPopTestStateContext::Idle,
    "Working" => TransitionPopTestStateContext::Working,
    _ => TransitionPopTestStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = TransitionPopTestFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    TransitionPopTestStateContext::Idle => {}
    TransitionPopTestStateContext::Working => {}
    TransitionPopTestStateContext::Empty => {}
}
    }

    pub fn start(&mut self) {
let __e = TransitionPopTestFrameEvent::new("start");
self.__kernel(__e);
    }

    pub fn process(&mut self) {
let __e = TransitionPopTestFrameEvent::new("process");
self.__kernel(__e);
    }

    pub fn get_state(&mut self) -> String {
let __e = TransitionPopTestFrameEvent::new("get_state");
match self.__compartment.state.as_str() {
            "Idle" => self._s_Idle_get_state(&__e),
            "Working" => self._s_Working_get_state(&__e),
            _ => Default::default(),
        }
    }

    pub fn get_log(&mut self) -> Vec<String> {
let __e = TransitionPopTestFrameEvent::new("get_log");
match self.__compartment.state.as_str() {
            "Idle" => self._s_Idle_get_log(&__e),
            "Working" => self._s_Working_get_log(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Working(&mut self, __e: &TransitionPopTestFrameEvent) {
match __e.message.as_str() {
    "get_log" => { self._s_Working_get_log(__e); }
    "get_state" => { self._s_Working_get_state(__e); }
    "process" => { self._s_Working_process(__e); }
    _ => {}
}
    }

    fn _state_Idle(&mut self, __e: &TransitionPopTestFrameEvent) {
match __e.message.as_str() {
    "get_log" => { self._s_Idle_get_log(__e); }
    "get_state" => { self._s_Idle_get_state(__e); }
    "process" => { self._s_Idle_process(__e); }
    "start" => { self._s_Idle_start(__e); }
    _ => {}
}
    }

    fn _s_Working_process(&mut self, __e: &TransitionPopTestFrameEvent) {
self.log.push("working:process:before_pop".to_string());
self._state_stack_pop();
return;
// This should NOT execute because pop transitions away
self.log.push("working:process:after_pop".to_string());
    }

    fn _s_Working_get_log(&mut self, __e: &TransitionPopTestFrameEvent) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Working_get_state(&mut self, __e: &TransitionPopTestFrameEvent) -> String {
return "Working".to_string();
    }

    fn _s_Idle_process(&mut self, __e: &TransitionPopTestFrameEvent) {
self.log.push("idle:process".to_string());
    }

    fn _s_Idle_get_log(&mut self, __e: &TransitionPopTestFrameEvent) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Idle_start(&mut self, __e: &TransitionPopTestFrameEvent) {
self.log.push("idle:start:push".to_string());
self._state_stack_push();
self.__transition(TransitionPopTestCompartment::new("Working"));
    }

    fn _s_Idle_get_state(&mut self, __e: &TransitionPopTestFrameEvent) -> String {
return "Idle".to_string();
    }
}


fn main() {
    println!("=== Test 20: Transition Pop (Rust) ===");
    let mut s = TransitionPopTest::new();

    // Initial state should be Idle
    assert_eq!(s.get_state(), "Idle", "Expected 'Idle'");
    println!("Initial state: {}", s.get_state());

    // start() pushes Idle, transitions to Working
    s.start();
    assert_eq!(s.get_state(), "Working", "Expected 'Working'");
    println!("After start(): {}", s.get_state());

    // process() in Working does pop transition back to Idle
    s.process();
    assert_eq!(s.get_state(), "Idle", "Expected 'Idle' after pop");
    println!("After process() with pop: {}", s.get_state());

    let log = s.get_log();
    println!("Log: {:?}", log);

    // Verify log contents
    assert!(log.contains(&"idle:start:push".to_string()), "Expected 'idle:start:push' in log");
    assert!(log.contains(&"working:process:before_pop".to_string()), "Expected 'working:process:before_pop' in log");
    assert!(!log.contains(&"working:process:after_pop".to_string()), "Should NOT have 'working:process:after_pop' in log");

    println!("PASS: Transition pop works correctly");
}
