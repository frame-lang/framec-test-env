use std::collections::HashMap;

pub struct PersistRoundtrip {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    counter: i32,
    mode: String,
}

impl PersistRoundtrip {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            counter: 0,
            mode: String::from("normal"),
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

    pub fn go_active(&mut self) {
match self._state.as_str() {
            "Idle" => { self._s_Idle_go_active(); }
            "Active" => { self._s_Active_go_active(); }
            _ => {}
        }
    }

    pub fn go_idle(&mut self) {
match self._state.as_str() {
            "Idle" => { self._s_Idle_go_idle(); }
            "Active" => { self._s_Active_go_idle(); }
            _ => {}
        }
    }

    pub fn get_state(&mut self) -> String {
match self._state.as_str() {
            "Idle" => self._s_Idle_get_state(),
            "Active" => self._s_Active_get_state(),
            _ => Default::default(),
        }
    }

    pub fn set_counter(&mut self, n: i32) {
match self._state.as_str() {
            "Idle" => { self._s_Idle_set_counter(n); }
            "Active" => { self._s_Active_set_counter(n); }
            _ => {}
        }
    }

    pub fn get_counter(&mut self) -> i32 {
match self._state.as_str() {
            "Idle" => self._s_Idle_get_counter(),
            "Active" => self._s_Active_get_counter(),
            _ => Default::default(),
        }
    }

    pub fn set_mode(&mut self, m: String) {
match self._state.as_str() {
            "Idle" => { self._s_Idle_set_mode(m); }
            "Active" => { self._s_Active_set_mode(m); }
            _ => {}
        }
    }

    pub fn get_mode(&mut self) -> String {
match self._state.as_str() {
            "Idle" => self._s_Idle_get_mode(),
            "Active" => self._s_Active_get_mode(),
            _ => Default::default(),
        }
    }

    fn _s_Idle_get_mode(&mut self) -> String {
return self.mode.clone();
    }

    fn _s_Idle_get_state(&mut self) -> String {
return String::from("idle");
    }

    fn _s_Idle_set_counter(&mut self, n: i32) {
self.counter = n;
    }

    fn _s_Idle_get_counter(&mut self) -> i32 {
return self.counter;
    }

    fn _s_Idle_go_active(&mut self) {
self._transition("Active");
    }

    fn _s_Idle_go_idle(&mut self) {
// already idle;
    }

    fn _s_Idle_set_mode(&mut self, m: String) {
self.mode = m;
    }

    fn _s_Active_get_counter(&mut self) -> i32 {
return self.counter;
    }

    fn _s_Active_get_state(&mut self) -> String {
return String::from("active");
    }

    fn _s_Active_go_idle(&mut self) {
self._transition("Idle");
    }

    fn _s_Active_set_counter(&mut self, n: i32) {
self.counter = n * 2;
    }

    fn _s_Active_set_mode(&mut self, m: String) {
self.mode = m;
    }

    fn _s_Active_go_active(&mut self) {
// already active;
    }

    fn _s_Active_get_mode(&mut self) -> String {
return self.mode.clone();
    }

    pub fn save_state(&mut self) -> String {
let stack_states: Vec<String> = self._state_stack.iter()
    .filter_map(|b| b.downcast_ref::<String>().cloned())
    .collect();
serde_json::json!({
    "_state": self._state,
    "_state_stack": stack_states,
    "counter": self.counter,
    "mode": self.mode,
}).to_string()
    }

    pub fn restore_state(json: &str) -> PersistRoundtrip {
let data: serde_json::Value = serde_json::from_str(json).unwrap();
let stack: Vec<Box<dyn std::any::Any>> = data["_state_stack"].as_array()
    .map(|arr| arr.iter()
        .filter_map(|v| v.as_str().map(|s| Box::new(s.to_string()) as Box<dyn std::any::Any>))
        .collect())
    .unwrap_or_default();
let mut instance = PersistRoundtrip {
    _state: data["_state"].as_str().unwrap().to_string(),
    _state_stack: stack,
    _state_context: std::collections::HashMap::new(),
    counter: serde_json::from_value(data["counter"].clone()).unwrap(),
    mode: data["mode"].as_str().unwrap().to_string(),
};
instance
    }
}


fn main() {
    println!("=== Test 24: Persist Roundtrip (Rust) ===");

    // Test 1: Create system and build up state
    let mut s1 = PersistRoundtrip::new();
    s1.set_counter(5);
    s1.set_mode(String::from("test"));
    s1.go_active();
    s1.set_counter(3);  // Should be 6 in Active (doubled)

    assert_eq!(s1.get_state(), "active", "Expected active state");
    assert_eq!(s1.get_counter(), 6, "Expected counter 6");
    assert_eq!(s1.get_mode(), "test", "Expected mode test");
    println!("1. State before save: state={}, counter={}, mode={}",
        s1.get_state(), s1.get_counter(), s1.get_mode());

    // Test 2: Save state
    let json = s1.save_state();
    println!("2. Saved JSON: {}", json);
    assert!(json.contains("Active"), "Expected Active in JSON");
    assert!(json.contains("6"), "Expected counter 6 in JSON");
    assert!(json.contains("test"), "Expected mode test in JSON");

    // Test 3: Restore to new instance
    let mut s2 = PersistRoundtrip::restore_state(&json);

    // Verify restored state matches
    assert_eq!(s2.get_state(), "active", "Restored: expected active state");
    assert_eq!(s2.get_counter(), 6, "Restored: expected counter 6");
    assert_eq!(s2.get_mode(), "test", "Restored: expected mode test");
    println!("3. Restored state: state={}, counter={}, mode={}",
        s2.get_state(), s2.get_counter(), s2.get_mode());

    // Test 4: State machine continues to work after restore
    s2.set_counter(2);  // Should be 4 in Active (doubled)
    assert_eq!(s2.get_counter(), 4, "Expected 4 after set_counter(2)");
    println!("4. Counter after set_counter(2): {}", s2.get_counter());

    // Test 5: Transitions work after restore
    s2.go_idle();
    assert_eq!(s2.get_state(), "idle", "Expected idle after go_idle");
    s2.set_counter(10);  // Not doubled in Idle
    assert_eq!(s2.get_counter(), 10, "Expected 10 in Idle");
    println!("5. After go_idle: state={}, counter={}", s2.get_state(), s2.get_counter());

    // Test 6: Save and restore again
    let json2 = s2.save_state();
    let mut s3 = PersistRoundtrip::restore_state(&json2);
    assert_eq!(s3.get_state(), "idle", "s3: expected idle");
    assert_eq!(s3.get_counter(), 10, "s3: expected counter 10");
    println!("6. Double restore works: state={}, counter={}", s3.get_state(), s3.get_counter());

    println!("PASS: Persist roundtrip works correctly");
}

