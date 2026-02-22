use std::collections::HashMap;

#[derive(Clone, Debug)]
struct ForwardEnterFirstFrameEvent {
    message: String,
}

impl ForwardEnterFirstFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct ForwardEnterFirstCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<ForwardEnterFirstFrameEvent>,
}

impl ForwardEnterFirstCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone, Default)]
struct WorkingContext {
    counter: i32,
}

#[derive(Clone)]
enum ForwardEnterFirstStateContext {
    Idle,
    Working(WorkingContext),
    Empty,
}

impl Default for ForwardEnterFirstStateContext {
    fn default() -> Self {
        ForwardEnterFirstStateContext::Idle
    }
}

pub struct ForwardEnterFirst {
    _state_stack: Vec<(String, ForwardEnterFirstStateContext)>,
    __compartment: ForwardEnterFirstCompartment,
    __next_compartment: Option<ForwardEnterFirstCompartment>,
    log: Vec<String>,
    _sv_counter: i32,
}

impl ForwardEnterFirst {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            log: Vec::new(),
            _sv_counter: 0,
            __compartment: ForwardEnterFirstCompartment::new("Idle"),
            __next_compartment: None,
        };
let __frame_event = ForwardEnterFirstFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: ForwardEnterFirstFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = ForwardEnterFirstFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = ForwardEnterFirstFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = ForwardEnterFirstFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &ForwardEnterFirstFrameEvent) {
match self.__compartment.state.as_str() {
    "Idle" => self._state_Idle(__e),
    "Working" => self._state_Working(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: ForwardEnterFirstCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Idle" => ForwardEnterFirstStateContext::Idle,
    "Working" => ForwardEnterFirstStateContext::Working(WorkingContext { counter: self._sv_counter }),
    _ => ForwardEnterFirstStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = ForwardEnterFirstFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    ForwardEnterFirstStateContext::Idle => {}
    ForwardEnterFirstStateContext::Working(ctx) => {
        self._sv_counter = ctx.counter;
    }
    ForwardEnterFirstStateContext::Empty => {}
}
    }

    pub fn process(&mut self) {
let __e = ForwardEnterFirstFrameEvent::new("process");
self.__kernel(__e);
    }

    pub fn get_counter(&mut self) -> i32 {
let __e = ForwardEnterFirstFrameEvent::new("get_counter");
match self.__compartment.state.as_str() {
            "Idle" => self._s_Idle_get_counter(&__e),
            "Working" => self._s_Working_get_counter(&__e),
            _ => Default::default(),
        }
    }

    pub fn get_log(&mut self) -> Vec<String> {
let __e = ForwardEnterFirstFrameEvent::new("get_log");
match self.__compartment.state.as_str() {
            "Idle" => self._s_Idle_get_log(&__e),
            "Working" => self._s_Working_get_log(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Idle(&mut self, __e: &ForwardEnterFirstFrameEvent) {
match __e.message.as_str() {
    "get_counter" => { self._s_Idle_get_counter(__e); }
    "get_log" => { self._s_Idle_get_log(__e); }
    "process" => { self._s_Idle_process(__e); }
    _ => {}
}
    }

    fn _state_Working(&mut self, __e: &ForwardEnterFirstFrameEvent) {
match __e.message.as_str() {
    "$>" => {
        self._sv_counter = 100;
        self._s_Working_enter(__e);
    }
    "get_counter" => { self._s_Working_get_counter(__e); }
    "get_log" => { self._s_Working_get_log(__e); }
    "process" => { self._s_Working_process(__e); }
    _ => {}
}
    }

    fn _s_Idle_get_log(&mut self, __e: &ForwardEnterFirstFrameEvent) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Idle_process(&mut self, __e: &ForwardEnterFirstFrameEvent) {
let mut __compartment = ForwardEnterFirstCompartment::new("Working");
__compartment.forward_event = Some(__e.clone());
self.__transition(__compartment);
return;
    }

    fn _s_Idle_get_counter(&mut self, __e: &ForwardEnterFirstFrameEvent) -> i32 {
return -1;
    }

    fn _s_Working_get_log(&mut self, __e: &ForwardEnterFirstFrameEvent) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Working_enter(&mut self, __e: &ForwardEnterFirstFrameEvent) {
self.log.push("Working:enter".to_string());
    }

    fn _s_Working_process(&mut self, __e: &ForwardEnterFirstFrameEvent) {
self.log.push(format!("Working:process:counter={}", self._sv_counter));
self._sv_counter = self._sv_counter + 1;
    }

    fn _s_Working_get_counter(&mut self, __e: &ForwardEnterFirstFrameEvent) -> i32 {
return self._sv_counter;
    }
}


fn main() {
    println!("=== Test 29: Forward Enter First (Rust) ===");
    let mut s = ForwardEnterFirst::new();

    // Initial state is Idle
    assert_eq!(s.get_counter(), -1, "Expected -1 in Idle");

    // Call process - should forward to Working
    // Correct behavior: $> runs first (inits counter=100, logs "Working:enter")
    // Then process runs (logs "Working:process:counter=100", increments to 101)
    s.process();

    // Check counter was initialized and incremented
    let counter = s.get_counter();
    let log = s.get_log();
    println!("Counter after forward: {}", counter);
    println!("Log: {:?}", log);

    // Verify $> ran first
    assert!(log.contains(&"Working:enter".to_string()),
            "Expected 'Working:enter' in log: {:?}", log);

    // Verify process ran after $>
    assert!(log.contains(&"Working:process:counter=100".to_string()),
            "Expected 'Working:process:counter=100' in log: {:?}", log);

    // Verify counter was incremented
    assert_eq!(counter, 101, "Expected counter=101, got {}", counter);

    // Verify order: enter before process
    let enter_idx = log.iter().position(|x| x == "Working:enter").unwrap();
    let process_idx = log.iter().position(|x| x == "Working:process:counter=100").unwrap();
    assert!(enter_idx < process_idx, "$> should run before process: {:?}", log);

    println!("PASS: Forward sends $> first for non-$> events");
}
