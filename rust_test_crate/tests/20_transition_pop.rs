use std::collections::HashMap;

pub struct TransitionPopTest {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    log: Vec<String>,
}

impl TransitionPopTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            log: Vec::new(),
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
        // No enter handlers
    }

    fn _exit(&mut self) {
        // No exit handlers
    }

    pub fn start(&mut self) {
match self._state.as_str() {
            "Idle" => { self._s_Idle_start(); }
            _ => {}
        }
    }

    pub fn process(&mut self) {
match self._state.as_str() {
            "Idle" => { self._s_Idle_process(); }
            "Working" => { self._s_Working_process(); }
            _ => {}
        }
    }

    pub fn get_state(&mut self) -> String {
match self._state.as_str() {
            "Idle" => self._s_Idle_get_state(),
            "Working" => self._s_Working_get_state(),
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
self.log.push("idle:process".to_string());
    }

    fn _s_Idle_get_state(&mut self) -> String {
return "Idle".to_string();
    }

    fn _s_Idle_get_log(&mut self) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Idle_start(&mut self) {
self.log.push("idle:start:push".to_string());
self._state_stack.push(Box::new(self._state.clone()));
self._transition("Working");
    }

    fn _s_Working_get_state(&mut self) -> String {
return "Working".to_string();
    }

    fn _s_Working_get_log(&mut self) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Working_process(&mut self) {
self.log.push("working:process:before_pop".to_string());
let __popped_state = *self._state_stack.pop().unwrap().downcast::<String>().unwrap();
self._transition(&__popped_state);
return;
// This should NOT execute because pop transitions away
self.log.push("working:process:after_pop".to_string());
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
