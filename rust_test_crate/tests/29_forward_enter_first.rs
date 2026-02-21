use std::collections::HashMap;

#[derive(Clone, Default)]
struct WorkingContext {
    counter: i32,
}

#[derive(Clone)]
enum ForwardEnterFirstCompartment {
    Idle,
    Working(WorkingContext),
    Empty,
}

impl Default for ForwardEnterFirstCompartment {
    fn default() -> Self {
        ForwardEnterFirstCompartment::Idle
    }
}

pub struct ForwardEnterFirst {
    _state: String,
    _state_stack: Vec<(String, ForwardEnterFirstCompartment)>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    log: Vec<String>,
    _sv_counter: i32,
}

impl ForwardEnterFirst {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            log: Vec::new(),
            _sv_counter: 0,
            _state: String::from("Idle"),
        };
        this._enter();
        this
    }

    fn _transition(&mut self, target_state: &str) {
        self._exit();
        self._state = target_state.to_string();
        self._enter();
    }

    fn _dispatch_event(&mut self, event: &str) {
let handler_name = format!("_s_{}_{}", self._state, event);
// Rust requires match-based dispatch or a handler registry
// For now, use explicit match in caller;
    }

    fn _enter(&mut self) {
match self._state.as_str() {
    "Working" => {
        self._sv_counter = 100;
        self._s_Working_enter();
    }
    _ => {}
}
    }

    fn _exit(&mut self) {
        // No exit handlers
    }

    fn _state_stack_push(&mut self) {
let compartment = match self._state.as_str() {
    "Idle" => ForwardEnterFirstCompartment::Idle,
    "Working" => ForwardEnterFirstCompartment::Working(WorkingContext { counter: self._sv_counter }),
    _ => ForwardEnterFirstCompartment::Empty,
};
self._state_stack.push((self._state.clone(), compartment));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, compartment) = self._state_stack.pop().unwrap();
self._exit();
self._state = saved_state;
match compartment {
    ForwardEnterFirstCompartment::Idle => {}
    ForwardEnterFirstCompartment::Working(ctx) => {
        self._sv_counter = ctx.counter;
    }
    ForwardEnterFirstCompartment::Empty => {}
}
    }

    pub fn process(&mut self) {
match self._state.as_str() {
            "Idle" => { self._s_Idle_process(); }
            "Working" => { self._s_Working_process(); }
            _ => {}
        }
    }

    pub fn get_counter(&mut self) -> i32 {
match self._state.as_str() {
            "Idle" => self._s_Idle_get_counter(),
            "Working" => self._s_Working_get_counter(),
            _ => Default::default(),
        }
    }

    pub fn get_log(&mut self) -> Vec<String> {
match self._state.as_str() {
            "Idle" => self._s_Idle_get_log(),
            "Working" => self._s_Working_get_log(),
            _ => Default::default(),
        }
    }

    fn _s_Idle_process(&mut self) {
self._transition("Working");
return self._s_Working_process();
    }

    fn _s_Idle_get_counter(&mut self) -> i32 {
return -1;
    }

    fn _s_Idle_get_log(&mut self) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Working_get_counter(&mut self) -> i32 {
return self._sv_counter;
    }

    fn _s_Working_get_log(&mut self) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Working_enter(&mut self) {
self.log.push("Working:enter".to_string());
    }

    fn _s_Working_process(&mut self) {
self.log.push(format!("Working:process:counter={}", self._sv_counter));
self._sv_counter = self._sv_counter + 1;
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
