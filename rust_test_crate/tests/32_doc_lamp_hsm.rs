
// Documentation Example: HSM Lamp with color behavior factored out


use std::collections::HashMap;

#[derive(Clone, Debug)]
struct LampHSMFrameEvent {
    message: String,
}

impl LampHSMFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct LampHSMCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<LampHSMFrameEvent>,
}

impl LampHSMCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum LampHSMStateContext {
    Off,
    On,
    ColorBehavior,
    Empty,
}

impl Default for LampHSMStateContext {
    fn default() -> Self {
        LampHSMStateContext::Off
    }
}

pub struct LampHSM {
    _state_stack: Vec<(String, LampHSMStateContext)>,
    __compartment: LampHSMCompartment,
    __next_compartment: Option<LampHSMCompartment>,
    color: String,
    lamp_on: bool,
}

impl LampHSM {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            color: String::from("white"),
            lamp_on: false,
            __compartment: LampHSMCompartment::new("Off"),
            __next_compartment: None,
        };
let __frame_event = LampHSMFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: LampHSMFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = LampHSMFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = LampHSMFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = LampHSMFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &LampHSMFrameEvent) {
match self.__compartment.state.as_str() {
    "Off" => self._state_Off(__e),
    "On" => self._state_On(__e),
    "ColorBehavior" => self._state_ColorBehavior(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: LampHSMCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Off" => LampHSMStateContext::Off,
    "On" => LampHSMStateContext::On,
    "ColorBehavior" => LampHSMStateContext::ColorBehavior,
    _ => LampHSMStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = LampHSMFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    LampHSMStateContext::Off => {}
    LampHSMStateContext::On => {}
    LampHSMStateContext::ColorBehavior => {}
    LampHSMStateContext::Empty => {}
}
    }

    pub fn turn_on(&mut self) {
let __e = LampHSMFrameEvent::new("turn_on");
self.__kernel(__e);
    }

    pub fn turn_off(&mut self) {
let __e = LampHSMFrameEvent::new("turn_off");
self.__kernel(__e);
    }

    pub fn get_color(&mut self) -> String {
let __e = LampHSMFrameEvent::new("get_color");
match self.__compartment.state.as_str() {
            "Off" => self._s_ColorBehavior_get_color(&__e),
            "On" => self._s_ColorBehavior_get_color(&__e),
            "ColorBehavior" => self._s_ColorBehavior_get_color(&__e),
            _ => Default::default(),
        }
    }

    pub fn set_color(&mut self, color: String) {
let __e = LampHSMFrameEvent::new("set_color");
match self.__compartment.state.as_str() {
            "Off" => { self._s_ColorBehavior_set_color(&__e, color); }
            "On" => { self._s_ColorBehavior_set_color(&__e, color); }
            "ColorBehavior" => { self._s_ColorBehavior_set_color(&__e, color); }
            _ => {}
        }
// Process any pending transitions (bypassed kernel)
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = LampHSMFrameEvent::new("$<");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = LampHSMFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = LampHSMFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    pub fn is_lamp_on(&mut self) -> bool {
let __e = LampHSMFrameEvent::new("is_lamp_on");
match self.__compartment.state.as_str() {
            "Off" => self._s_Off_is_lamp_on(&__e),
            "On" => self._s_On_is_lamp_on(&__e),
            _ => Default::default(),
        }
    }

    fn _state_ColorBehavior(&mut self, __e: &LampHSMFrameEvent) {
match __e.message.as_str() {
    "get_color" => { self._s_ColorBehavior_get_color(__e); }
    _ => {}
}
    }

    fn _state_Off(&mut self, __e: &LampHSMFrameEvent) {
match __e.message.as_str() {
    "is_lamp_on" => { self._s_Off_is_lamp_on(__e); }
    "turn_on" => { self._s_Off_turn_on(__e); }
    _ => self._state_ColorBehavior(__e),
}
    }

    fn _state_On(&mut self, __e: &LampHSMFrameEvent) {
match __e.message.as_str() {
    "$<" => { self._s_On_exit(__e); }
    "$>" => { self._s_On_enter(__e); }
    "is_lamp_on" => { self._s_On_is_lamp_on(__e); }
    "turn_off" => { self._s_On_turn_off(__e); }
    _ => self._state_ColorBehavior(__e),
}
    }

    fn _s_ColorBehavior_get_color(&mut self, __e: &LampHSMFrameEvent) -> String {
return self.color.clone()
    }

    fn _s_ColorBehavior_set_color(&mut self, __e: &LampHSMFrameEvent, color: String) {
self.color = color;
    }

    fn _s_Off_turn_on(&mut self, __e: &LampHSMFrameEvent) {
self.__transition(LampHSMCompartment::new("On"));
    }

    fn _s_Off_is_lamp_on(&mut self, __e: &LampHSMFrameEvent) -> bool {
return self.lamp_on
    }

    fn _s_On_is_lamp_on(&mut self, __e: &LampHSMFrameEvent) -> bool {
return self.lamp_on
    }

    fn _s_On_exit(&mut self, __e: &LampHSMFrameEvent) {
self.turn_off_lamp();
    }

    fn _s_On_enter(&mut self, __e: &LampHSMFrameEvent) {
self.turn_on_lamp();
    }

    fn _s_On_turn_off(&mut self, __e: &LampHSMFrameEvent) {
self.__transition(LampHSMCompartment::new("Off"));
    }

    fn turn_on_lamp(&mut self) {
            self.lamp_on = true;
    }

    fn turn_off_lamp(&mut self) {
            self.lamp_on = false;
    }
}


fn main() {
    println!("=== Test 32: Doc Lamp HSM ===");
    let mut lamp = LampHSM::new();

    // Color behavior available in both states
    assert_eq!(lamp.get_color(), "white", "Expected 'white'");
    lamp.set_color(String::from("red"));
    assert_eq!(lamp.get_color(), "red", "Expected 'red'");

    // Turn on
    lamp.turn_on();
    assert!(lamp.is_lamp_on(), "Lamp should be on");

    // Color still works when on
    lamp.set_color(String::from("green"));
    assert_eq!(lamp.get_color(), "green", "Expected 'green'");

    // Turn off
    lamp.turn_off();
    assert!(!lamp.is_lamp_on(), "Lamp should be off");

    // Color still works when off
    assert_eq!(lamp.get_color(), "green", "Expected 'green'");

    println!("PASS: HSM lamp works correctly");
}
