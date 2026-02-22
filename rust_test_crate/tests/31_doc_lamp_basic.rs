
// Documentation Example: Basic Lamp with enter/exit events


use std::collections::HashMap;

#[derive(Clone, Debug)]
struct LampFrameEvent {
    message: String,
}

impl LampFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct LampCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<LampFrameEvent>,
}

impl LampCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum LampStateContext {
    Off,
    On,
    Empty,
}

impl Default for LampStateContext {
    fn default() -> Self {
        LampStateContext::Off
    }
}

pub struct Lamp {
    _state_stack: Vec<(String, LampStateContext)>,
    __compartment: LampCompartment,
    __next_compartment: Option<LampCompartment>,
    color: String,
    switch_closed: bool,
}

impl Lamp {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            color: String::from("white"),
            switch_closed: false,
            __compartment: LampCompartment::new("Off"),
            __next_compartment: None,
        };
let __frame_event = LampFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: LampFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = LampFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = LampFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = LampFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &LampFrameEvent) {
match self.__compartment.state.as_str() {
    "Off" => self._state_Off(__e),
    "On" => self._state_On(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: LampCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Off" => LampStateContext::Off,
    "On" => LampStateContext::On,
    _ => LampStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = LampFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    LampStateContext::Off => {}
    LampStateContext::On => {}
    LampStateContext::Empty => {}
}
    }

    pub fn turn_on(&mut self) {
let __e = LampFrameEvent::new("turn_on");
self.__kernel(__e);
    }

    pub fn turn_off(&mut self) {
let __e = LampFrameEvent::new("turn_off");
self.__kernel(__e);
    }

    pub fn get_color(&mut self) -> String {
let __e = LampFrameEvent::new("get_color");
match self.__compartment.state.as_str() {
            "Off" => self._s_Off_get_color(&__e),
            "On" => self._s_On_get_color(&__e),
            _ => Default::default(),
        }
    }

    pub fn set_color(&mut self, color: String) {
let __e = LampFrameEvent::new("set_color");
match self.__compartment.state.as_str() {
            "Off" => { self._s_Off_set_color(&__e, color); }
            "On" => { self._s_On_set_color(&__e, color); }
            _ => {}
        }
// Process any pending transitions (bypassed kernel)
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = LampFrameEvent::new("$<");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = LampFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = LampFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    pub fn is_switch_closed(&mut self) -> bool {
let __e = LampFrameEvent::new("is_switch_closed");
match self.__compartment.state.as_str() {
            "Off" => self._s_Off_is_switch_closed(&__e),
            "On" => self._s_On_is_switch_closed(&__e),
            _ => Default::default(),
        }
    }

    fn _state_On(&mut self, __e: &LampFrameEvent) {
match __e.message.as_str() {
    "$<" => { self._s_On_exit(__e); }
    "$>" => { self._s_On_enter(__e); }
    "get_color" => { self._s_On_get_color(__e); }
    "is_switch_closed" => { self._s_On_is_switch_closed(__e); }
    "turn_off" => { self._s_On_turn_off(__e); }
    _ => {}
}
    }

    fn _state_Off(&mut self, __e: &LampFrameEvent) {
match __e.message.as_str() {
    "get_color" => { self._s_Off_get_color(__e); }
    "is_switch_closed" => { self._s_Off_is_switch_closed(__e); }
    "turn_on" => { self._s_Off_turn_on(__e); }
    _ => {}
}
    }

    fn _s_On_get_color(&mut self, __e: &LampFrameEvent) -> String {
return self.color.clone()
    }

    fn _s_On_set_color(&mut self, __e: &LampFrameEvent, color: String) {
self.color = color;
    }

    fn _s_On_enter(&mut self, __e: &LampFrameEvent) {
self.close_switch();
    }

    fn _s_On_exit(&mut self, __e: &LampFrameEvent) {
self.open_switch();
    }

    fn _s_On_turn_off(&mut self, __e: &LampFrameEvent) {
self.__transition(LampCompartment::new("Off"));
    }

    fn _s_On_is_switch_closed(&mut self, __e: &LampFrameEvent) -> bool {
return self.switch_closed
    }

    fn _s_Off_turn_on(&mut self, __e: &LampFrameEvent) {
self.__transition(LampCompartment::new("On"));
    }

    fn _s_Off_get_color(&mut self, __e: &LampFrameEvent) -> String {
return self.color.clone()
    }

    fn _s_Off_set_color(&mut self, __e: &LampFrameEvent, color: String) {
self.color = color;
    }

    fn _s_Off_is_switch_closed(&mut self, __e: &LampFrameEvent) -> bool {
return self.switch_closed
    }

    fn close_switch(&mut self) {
            self.switch_closed = true;
    }

    fn open_switch(&mut self) {
            self.switch_closed = false;
    }
}


fn main() {
    println!("=== Test 31: Doc Lamp Basic ===");
    let mut lamp = Lamp::new();

    // Initially off
    assert!(!lamp.is_switch_closed(), "Switch should be open initially");

    // Turn on - should close switch
    lamp.turn_on();
    assert!(lamp.is_switch_closed(), "Switch should be closed after turn_on");

    // Check color
    assert_eq!(lamp.get_color(), "white", "Expected 'white'");

    // Set color
    lamp.set_color(String::from("blue"));
    assert_eq!(lamp.get_color(), "blue", "Expected 'blue'");

    // Turn off - should open switch
    lamp.turn_off();
    assert!(!lamp.is_switch_closed(), "Switch should be open after turn_off");

    println!("PASS: Basic lamp works correctly");
}
