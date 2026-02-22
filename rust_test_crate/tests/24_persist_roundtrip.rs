use std::collections::HashMap;

#[derive(Clone, Debug)]
struct PersistRoundtripFrameEvent {
    message: String,
}

impl PersistRoundtripFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct PersistRoundtripCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<PersistRoundtripFrameEvent>,
}

impl PersistRoundtripCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum PersistRoundtripStateContext {
    Idle,
    Active,
    Empty,
}

impl Default for PersistRoundtripStateContext {
    fn default() -> Self {
        PersistRoundtripStateContext::Idle
    }
}

pub struct PersistRoundtrip {
    _state_stack: Vec<(String, PersistRoundtripStateContext)>,
    __compartment: PersistRoundtripCompartment,
    __next_compartment: Option<PersistRoundtripCompartment>,
    counter: i32,
    mode: String,
}

impl PersistRoundtrip {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            counter: 0,
            mode: String::from("normal"),
            __compartment: PersistRoundtripCompartment::new("Idle"),
            __next_compartment: None,
        };
let __frame_event = PersistRoundtripFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: PersistRoundtripFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = PersistRoundtripFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = PersistRoundtripFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = PersistRoundtripFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &PersistRoundtripFrameEvent) {
match self.__compartment.state.as_str() {
    "Idle" => self._state_Idle(__e),
    "Active" => self._state_Active(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: PersistRoundtripCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Idle" => PersistRoundtripStateContext::Idle,
    "Active" => PersistRoundtripStateContext::Active,
    _ => PersistRoundtripStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = PersistRoundtripFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    PersistRoundtripStateContext::Idle => {}
    PersistRoundtripStateContext::Active => {}
    PersistRoundtripStateContext::Empty => {}
}
    }

    pub fn go_active(&mut self) {
let __e = PersistRoundtripFrameEvent::new("go_active");
self.__kernel(__e);
    }

    pub fn go_idle(&mut self) {
let __e = PersistRoundtripFrameEvent::new("go_idle");
self.__kernel(__e);
    }

    pub fn get_state(&mut self) -> String {
let __e = PersistRoundtripFrameEvent::new("get_state");
match self.__compartment.state.as_str() {
            "Idle" => self._s_Idle_get_state(&__e),
            "Active" => self._s_Active_get_state(&__e),
            _ => Default::default(),
        }
    }

    pub fn set_counter(&mut self, n: i32) {
let __e = PersistRoundtripFrameEvent::new("set_counter");
match self.__compartment.state.as_str() {
            "Idle" => { self._s_Idle_set_counter(&__e, n); }
            "Active" => { self._s_Active_set_counter(&__e, n); }
            _ => {}
        }
// Process any pending transitions (bypassed kernel)
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = PersistRoundtripFrameEvent::new("$<");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = PersistRoundtripFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = PersistRoundtripFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    pub fn get_counter(&mut self) -> i32 {
let __e = PersistRoundtripFrameEvent::new("get_counter");
match self.__compartment.state.as_str() {
            "Idle" => self._s_Idle_get_counter(&__e),
            "Active" => self._s_Active_get_counter(&__e),
            _ => Default::default(),
        }
    }

    pub fn set_mode(&mut self, m: String) {
let __e = PersistRoundtripFrameEvent::new("set_mode");
match self.__compartment.state.as_str() {
            "Idle" => { self._s_Idle_set_mode(&__e, m); }
            "Active" => { self._s_Active_set_mode(&__e, m); }
            _ => {}
        }
// Process any pending transitions (bypassed kernel)
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = PersistRoundtripFrameEvent::new("$<");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = PersistRoundtripFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = PersistRoundtripFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    pub fn get_mode(&mut self) -> String {
let __e = PersistRoundtripFrameEvent::new("get_mode");
match self.__compartment.state.as_str() {
            "Idle" => self._s_Idle_get_mode(&__e),
            "Active" => self._s_Active_get_mode(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Active(&mut self, __e: &PersistRoundtripFrameEvent) {
match __e.message.as_str() {
    "get_counter" => { self._s_Active_get_counter(__e); }
    "get_mode" => { self._s_Active_get_mode(__e); }
    "get_state" => { self._s_Active_get_state(__e); }
    "go_active" => { self._s_Active_go_active(__e); }
    "go_idle" => { self._s_Active_go_idle(__e); }
    _ => {}
}
    }

    fn _state_Idle(&mut self, __e: &PersistRoundtripFrameEvent) {
match __e.message.as_str() {
    "get_counter" => { self._s_Idle_get_counter(__e); }
    "get_mode" => { self._s_Idle_get_mode(__e); }
    "get_state" => { self._s_Idle_get_state(__e); }
    "go_active" => { self._s_Idle_go_active(__e); }
    "go_idle" => { self._s_Idle_go_idle(__e); }
    _ => {}
}
    }

    fn _s_Active_set_counter(&mut self, __e: &PersistRoundtripFrameEvent, n: i32) {
self.counter = n * 2;
    }

    fn _s_Active_get_state(&mut self, __e: &PersistRoundtripFrameEvent) -> String {
return String::from("active");
    }

    fn _s_Active_get_mode(&mut self, __e: &PersistRoundtripFrameEvent) -> String {
return self.mode.clone();
    }

    fn _s_Active_go_idle(&mut self, __e: &PersistRoundtripFrameEvent) {
self.__transition(PersistRoundtripCompartment::new("Idle"));
    }

    fn _s_Active_get_counter(&mut self, __e: &PersistRoundtripFrameEvent) -> i32 {
return self.counter;
    }

    fn _s_Active_set_mode(&mut self, __e: &PersistRoundtripFrameEvent, m: String) {
self.mode = m;
    }

    fn _s_Active_go_active(&mut self, __e: &PersistRoundtripFrameEvent) {
// already active;
    }

    fn _s_Idle_get_state(&mut self, __e: &PersistRoundtripFrameEvent) -> String {
return String::from("idle");
    }

    fn _s_Idle_go_active(&mut self, __e: &PersistRoundtripFrameEvent) {
self.__transition(PersistRoundtripCompartment::new("Active"));
    }

    fn _s_Idle_set_mode(&mut self, __e: &PersistRoundtripFrameEvent, m: String) {
self.mode = m;
    }

    fn _s_Idle_go_idle(&mut self, __e: &PersistRoundtripFrameEvent) {
// already idle;
    }

    fn _s_Idle_set_counter(&mut self, __e: &PersistRoundtripFrameEvent, n: i32) {
self.counter = n;
    }

    fn _s_Idle_get_counter(&mut self, __e: &PersistRoundtripFrameEvent) -> i32 {
return self.counter;
    }

    fn _s_Idle_get_mode(&mut self, __e: &PersistRoundtripFrameEvent) -> String {
return self.mode.clone();
    }

    pub fn save_state(&mut self) -> String {
let stack_states: Vec<&str> = self._state_stack.iter().map(|(s, _)| s.as_str()).collect();
serde_json::json!({
    "_state": self.__compartment.state,
    "_state_stack": stack_states,
    "counter": self.counter,
    "mode": self.mode,
}).to_string()
    }

    pub fn restore_state(json: &str) -> PersistRoundtrip {
let data: serde_json::Value = serde_json::from_str(json).unwrap();
let stack: Vec<(String, PersistRoundtripStateContext)> = data["_state_stack"].as_array()
    .map(|arr| arr.iter()
        .filter_map(|v| v.as_str().map(|s| (s.to_string(), PersistRoundtripStateContext::Empty)))
        .collect())
    .unwrap_or_default();
let mut instance = PersistRoundtrip {
    _state_stack: stack,
    __compartment: PersistRoundtripCompartment::new(data["_state"].as_str().unwrap()),
    __next_compartment: None,
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
