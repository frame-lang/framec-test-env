use std::collections::HashMap;

pub struct HSMDefaultForward {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    log: Vec<String>,
}

impl HSMDefaultForward {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            log: Vec::new(),
            _state: String::from("Child"),
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

    pub fn handled_event(&mut self) {
match self._state.as_str() {
            "Child" => { self._s_Child_handled_event(); }
            "Parent" => { self._s_Parent_handled_event(); }
            _ => {}
        }
    }

    pub fn unhandled_event(&mut self) {
match self._state.as_str() {
            "Child" => { self._s_Parent_unhandled_event(); }
            "Parent" => { self._s_Parent_unhandled_event(); }
            _ => {}
        }
    }

    pub fn get_log(&mut self) -> Vec<String> {
match self._state.as_str() {
            "Child" => self._s_Child_get_log(),
            "Parent" => self._s_Parent_get_log(),
            _ => Default::default(),
        }
    }

    fn _s_Parent_handled_event(&mut self) {
self.log.push("Parent:handled_event".to_string());
    }

    fn _s_Parent_unhandled_event(&mut self) {
self.log.push("Parent:unhandled_event".to_string());
    }

    fn _s_Parent_get_log(&mut self) -> Vec<String> {
return self.log.clone();
    }

    fn _s_Child_handled_event(&mut self) {
self.log.push("Child:handled_event".to_string());
    }

    fn _s_Child_get_log(&mut self) -> Vec<String> {
return self.log.clone();
    }
}


fn main() {
    println!("=== Test 30: HSM State-Level Default Forward (Rust) ===");
    let mut s = HSMDefaultForward::new();

    s.handled_event();
    let log = s.get_log();
    assert!(log.contains(&"Child:handled_event".to_string()),
            "Expected 'Child:handled_event' in log, got {:?}", log);
    println!("After handled_event: {:?}", log);

    s.unhandled_event();
    let log = s.get_log();
    assert!(log.contains(&"Parent:unhandled_event".to_string()),
            "Expected 'Parent:unhandled_event' in log (forwarded), got {:?}", log);
    println!("After unhandled_event (forwarded): {:?}", log);

    println!("PASS: HSM state-level default forward works correctly");
}
