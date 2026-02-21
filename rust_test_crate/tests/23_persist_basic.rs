use std::collections::HashMap;

pub struct PersistTest {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    value: i32,
    name: String,
}

impl PersistTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            value: 0,
            name: String::from("default"),
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

    pub fn set_value(&mut self, v: i32) {
match self._state.as_str() {
            "Idle" => { self._s_Idle_set_value(v); }
            "Active" => { self._s_Active_set_value(v); }
            _ => {}
        }
    }

    pub fn get_value(&mut self) -> i32 {
match self._state.as_str() {
            "Idle" => self._s_Idle_get_value(),
            "Active" => self._s_Active_get_value(),
            _ => Default::default(),
        }
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

    fn _s_Idle_set_value(&mut self, v: i32) {
self.value = v;
    }

    fn _s_Idle_go_active(&mut self) {
self._transition("Active");
    }

    fn _s_Idle_go_idle(&mut self) {
// Already idle;
    }

    fn _s_Idle_get_value(&mut self) -> i32 {
return self.value;
    }

    fn _s_Active_set_value(&mut self, v: i32) {
self.value = v * 2;
    }

    fn _s_Active_get_value(&mut self) -> i32 {
return self.value;
    }

    fn _s_Active_go_idle(&mut self) {
self._transition("Idle");
    }

    fn _s_Active_go_active(&mut self) {
// Already active;
    }

    pub fn save_state(&mut self) -> String {
let stack_states: Vec<String> = self._state_stack.iter()
    .filter_map(|b| b.downcast_ref::<String>().cloned())
    .collect();
serde_json::json!({
    "_state": self._state,
    "_state_stack": stack_states,
    "value": self.value,
    "name": self.name,
}).to_string()
    }

    pub fn restore_state(json: &str) -> PersistTest {
let data: serde_json::Value = serde_json::from_str(json).unwrap();
let stack: Vec<Box<dyn std::any::Any>> = data["_state_stack"].as_array()
    .map(|arr| arr.iter()
        .filter_map(|v| v.as_str().map(|s| Box::new(s.to_string()) as Box<dyn std::any::Any>))
        .collect())
    .unwrap_or_default();
let mut instance = PersistTest {
    _state: data["_state"].as_str().unwrap().to_string(),
    _state_stack: stack,
    _state_context: std::collections::HashMap::new(),
    value: serde_json::from_value(data["value"].clone()).unwrap(),
    name: data["name"].as_str().unwrap().to_string(),
};
instance
    }
}


fn main() {
    println!("=== Test 23: Persist Basic (Rust with serde) ===");

    // Test 1: Create and modify system
    let mut s1 = PersistTest::new();
    s1.set_value(10);
    s1.go_active();
    s1.set_value(5);  // Should be doubled to 10 in Active state

    // Test 2: Save state
    let json = s1.save_state();
    assert!(json.contains("Active"), "Expected Active state in JSON");
    assert!(json.contains("10"), "Expected value 10 in JSON");
    println!("1. Saved state: {}", json);

    // Test 3: Restore state
    let mut s2 = PersistTest::restore_state(&json);
    assert_eq!(s2.get_value(), 10, "Expected restored value 10");
    println!("2. Restored value: {}", s2.get_value());

    // Test 4: Verify state is preserved (Active state doubles)
    s2.set_value(3);  // Should be doubled to 6 in Active state
    assert_eq!(s2.get_value(), 6, "Expected 6 after set_value(3) in Active");
    println!("3. After set_value(3) in Active: {}", s2.get_value());

    // Test 5: Verify transitions work after restore
    s2.go_idle();
    s2.set_value(4);  // Should NOT be doubled in Idle state
    assert_eq!(s2.get_value(), 4, "Expected 4 after set_value(4) in Idle");
    println!("4. After go_idle, set_value(4): {}", s2.get_value());

    println!("PASS: Persist basic works correctly");
}
