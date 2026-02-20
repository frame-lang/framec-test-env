use std::collections::HashMap;

pub struct HSMForward {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    log: Vec<String>,
}

impl HSMForward {
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

    fn _change_state(&mut self, target_state: &str) {
        self._state = target_state.to_string();
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

    pub fn event_a(&mut self) {
match self._state.as_str() {
            "Child" => { self._s_Child_event_a(); }
            "Parent" => { self._s_Parent_event_a(); }
            _ => {}
        }
    }

    pub fn event_b(&mut self) {
match self._state.as_str() {
            "Child" => { self._s_Child_event_b(); }
            "Parent" => { self._s_Parent_event_b(); }
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

    fn _s_Child_event_a(&mut self) {
self.log.push("Child:event_a".to_string());
    }

    fn _s_Child_event_b(&mut self) {
self.log.push("Child:event_b_forward".to_string());
self._s_Parent_event_b();
    }

    fn _s_Child_get_log(&mut self) -> Vec<String> {
self.log.clone()
    }

    fn _s_Parent_get_log(&mut self) -> Vec<String> {
self.log.clone()
    }

    fn _s_Parent_event_b(&mut self) {
self.log.push("Parent:event_b".to_string());
    }

    fn _s_Parent_event_a(&mut self) {
self.log.push("Parent:event_a".to_string());
    }
}


fn main() {
    println!("=== Test 08: HSM Forward ===");
    let mut s = HSMForward::new();

    // event_a should be handled by Child (no forward)
    s.event_a();
    let log = s.get_log();
    assert!(log.contains(&"Child:event_a".to_string()), "Expected 'Child:event_a' in log, got {:?}", log);
    println!("After event_a: {:?}", log);

    // event_b should forward to Parent
    s.event_b();
    let log = s.get_log();
    assert!(log.contains(&"Child:event_b_forward".to_string()), "Expected 'Child:event_b_forward' in log, got {:?}", log);
    assert!(log.contains(&"Parent:event_b".to_string()), "Expected 'Parent:event_b' in log (forwarded), got {:?}", log);
    println!("After event_b (forwarded): {:?}", log);

    println!("PASS: HSM forward works correctly");
}

