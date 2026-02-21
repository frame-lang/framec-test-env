use std::collections::HashMap;

pub struct PersistStack {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    depth: i32,
}

impl PersistStack {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            depth: 0,
            _state: String::from("Start"),
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

    pub fn push_and_go(&mut self) {
match self._state.as_str() {
            "Start" => { self._s_Start_push_and_go(); }
            "Middle" => { self._s_Middle_push_and_go(); }
            "End" => { self._s_End_push_and_go(); }
            _ => {}
        }
    }

    pub fn pop_back(&mut self) {
match self._state.as_str() {
            "Start" => { self._s_Start_pop_back(); }
            "Middle" => { self._s_Middle_pop_back(); }
            "End" => { self._s_End_pop_back(); }
            _ => {}
        }
    }

    pub fn get_state(&mut self) -> String {
match self._state.as_str() {
            "Start" => self._s_Start_get_state(),
            "Middle" => self._s_Middle_get_state(),
            "End" => self._s_End_get_state(),
            _ => Default::default(),
        }
    }

    pub fn get_depth(&mut self) -> i32 {
match self._state.as_str() {
            "Start" => self._s_Start_get_depth(),
            "Middle" => self._s_Middle_get_depth(),
            "End" => self._s_End_get_depth(),
            _ => Default::default(),
        }
    }

    fn _s_Middle_get_state(&mut self) -> String {
return String::from("middle");
    }

    fn _s_Middle_get_depth(&mut self) -> i32 {
return self.depth;
    }

    fn _s_Middle_push_and_go(&mut self) {
self.depth = self.depth + 1;
self._state_stack.push(Box::new(self._state.clone()));
self._transition("End");
    }

    fn _s_Middle_pop_back(&mut self) {
self.depth = self.depth - 1;
let __popped_state = *self._state_stack.pop().unwrap().downcast::<String>().unwrap();
self._transition(&__popped_state);
return;
    }

    fn _s_End_pop_back(&mut self) {
self.depth = self.depth - 1;
let __popped_state = *self._state_stack.pop().unwrap().downcast::<String>().unwrap();
self._transition(&__popped_state);
return;
    }

    fn _s_End_push_and_go(&mut self) {
// can't go further;
    }

    fn _s_End_get_state(&mut self) -> String {
return String::from("end");
    }

    fn _s_End_get_depth(&mut self) -> i32 {
return self.depth;
    }

    fn _s_Start_push_and_go(&mut self) {
self.depth = self.depth + 1;
self._state_stack.push(Box::new(self._state.clone()));
self._transition("Middle");
    }

    fn _s_Start_get_state(&mut self) -> String {
return String::from("start");
    }

    fn _s_Start_pop_back(&mut self) {
// nothing to pop;
    }

    fn _s_Start_get_depth(&mut self) -> i32 {
return self.depth;
    }

    pub fn save_state(&mut self) -> String {
let stack_states: Vec<String> = self._state_stack.iter()
    .filter_map(|b| b.downcast_ref::<String>().cloned())
    .collect();
serde_json::json!({
    "_state": self._state,
    "_state_stack": stack_states,
    "depth": self.depth,
}).to_string()
    }

    pub fn restore_state(json: &str) -> PersistStack {
let data: serde_json::Value = serde_json::from_str(json).unwrap();
let stack: Vec<Box<dyn std::any::Any>> = data["_state_stack"].as_array()
    .map(|arr| arr.iter()
        .filter_map(|v| v.as_str().map(|s| Box::new(s.to_string()) as Box<dyn std::any::Any>))
        .collect())
    .unwrap_or_default();
let mut instance = PersistStack {
    _state: data["_state"].as_str().unwrap().to_string(),
    _state_stack: stack,
    _state_context: std::collections::HashMap::new(),
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
