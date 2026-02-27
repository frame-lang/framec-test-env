use std::collections::HashMap;

#[derive(Clone, Debug)]
struct PersistTestFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, String>,
}

impl PersistTestFrameEvent {
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

struct PersistTestFrameContext {
    event: PersistTestFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl PersistTestFrameContext {
    fn new(event: PersistTestFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct PersistTestCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<PersistTestFrameEvent>,
}

impl PersistTestCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum PersistTestStateContext {
    Idle,
    Active,
    Empty,
}

impl Default for PersistTestStateContext {
    fn default() -> Self {
        PersistTestStateContext::Idle
    }
}

pub struct PersistTest {
    _state_stack: Vec<(String, PersistTestStateContext)>,
    __compartment: PersistTestCompartment,
    __next_compartment: Option<PersistTestCompartment>,
    _context_stack: Vec<PersistTestFrameContext>,
    value: i32,
    name: String,
}

impl PersistTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            value: 0,
            name: String::from("default"),
            __compartment: PersistTestCompartment::new("Idle"),
            __next_compartment: None,
        };
let __frame_event = PersistTestFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: PersistTestFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = PersistTestFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = PersistTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = PersistTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &PersistTestFrameEvent) {
match self.__compartment.state.as_str() {
    "Idle" => self._state_Idle(__e),
    "Active" => self._state_Active(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: PersistTestCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Idle" => PersistTestStateContext::Idle,
    "Active" => PersistTestStateContext::Active,
    _ => PersistTestStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = PersistTestFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    PersistTestStateContext::Idle => {}
    PersistTestStateContext::Active => {}
    PersistTestStateContext::Empty => {}
}
    }

    pub fn set_value(&mut self, v: i32) {
let __e = PersistTestFrameEvent::new("set_value");
match self.__compartment.state.as_str() {
            "Idle" => { self._s_Idle_set_value(&__e, v); }
            "Active" => { self._s_Active_set_value(&__e, v); }
            _ => {}
        }
// Process any pending transitions (bypassed kernel)
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = PersistTestFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = PersistTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = PersistTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    pub fn get_value(&mut self) -> i32 {
let __e = PersistTestFrameEvent::new("get_value");
match self.__compartment.state.as_str() {
            "Idle" => self._s_Idle_get_value(&__e),
            "Active" => self._s_Active_get_value(&__e),
            _ => Default::default(),
        }
    }

    pub fn go_active(&mut self) {
let __e = PersistTestFrameEvent::new("go_active");
self.__kernel(__e);
    }

    pub fn go_idle(&mut self) {
let __e = PersistTestFrameEvent::new("go_idle");
self.__kernel(__e);
    }

    fn _state_Active(&mut self, __e: &PersistTestFrameEvent) {
match __e.message.as_str() {
    "get_value" => { self._s_Active_get_value(__e); }
    "go_active" => { self._s_Active_go_active(__e); }
    "go_idle" => { self._s_Active_go_idle(__e); }
    _ => {}
}
    }

    fn _state_Idle(&mut self, __e: &PersistTestFrameEvent) {
match __e.message.as_str() {
    "get_value" => { self._s_Idle_get_value(__e); }
    "go_active" => { self._s_Idle_go_active(__e); }
    "go_idle" => { self._s_Idle_go_idle(__e); }
    _ => {}
}
    }

    fn _s_Active_get_value(&mut self, __e: &PersistTestFrameEvent) -> i32 {
return self.value;
    }

    fn _s_Active_go_idle(&mut self, __e: &PersistTestFrameEvent) {
self.__transition(PersistTestCompartment::new("Idle"));
    }

    fn _s_Active_set_value(&mut self, __e: &PersistTestFrameEvent, v: i32) {
self.value = v * 2;
    }

    fn _s_Active_go_active(&mut self, __e: &PersistTestFrameEvent) {
// Already active;
    }

    fn _s_Idle_get_value(&mut self, __e: &PersistTestFrameEvent) -> i32 {
return self.value;
    }

    fn _s_Idle_set_value(&mut self, __e: &PersistTestFrameEvent, v: i32) {
self.value = v;
    }

    fn _s_Idle_go_idle(&mut self, __e: &PersistTestFrameEvent) {
// Already idle;
    }

    fn _s_Idle_go_active(&mut self, __e: &PersistTestFrameEvent) {
self.__transition(PersistTestCompartment::new("Active"));
    }

    pub fn save_state(&mut self) -> String {
let stack_states: Vec<&str> = self._state_stack.iter().map(|(s, _)| s.as_str()).collect();
serde_json::json!({
    "_state": self.__compartment.state,
    "_state_stack": stack_states,
    "value": self.value,
    "name": self.name,
}).to_string()
    }

    pub fn restore_state(json: &str) -> PersistTest {
let data: serde_json::Value = serde_json::from_str(json).unwrap();
let stack: Vec<(String, PersistTestStateContext)> = data["_state_stack"].as_array()
    .map(|arr| arr.iter()
        .filter_map(|v| v.as_str().map(|s| (s.to_string(), PersistTestStateContext::Empty)))
        .collect())
    .unwrap_or_default();
let mut instance = PersistTest {
    _state_stack: stack,
    __compartment: PersistTestCompartment::new(data["_state"].as_str().unwrap()),
    __next_compartment: None,
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
