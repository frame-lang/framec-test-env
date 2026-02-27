use std::collections::HashMap;

struct EnterExitFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl Clone for EnterExitFrameEvent {
    fn clone(&self) -> Self {
        Self {
            message: self.message.clone(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

impl EnterExitFrameEvent {
    fn new(message: &str) -> Self {
        Self {
            message: message.to_string(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

struct EnterExitFrameContext {
    event: EnterExitFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl EnterExitFrameContext {
    fn new(event: EnterExitFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct EnterExitCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<EnterExitFrameEvent>,
}

impl EnterExitCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum EnterExitStateContext {
    Off,
    On,
    Empty,
}

impl Default for EnterExitStateContext {
    fn default() -> Self {
        EnterExitStateContext::Off
    }
}

pub struct EnterExit {
    _state_stack: Vec<(String, EnterExitStateContext)>,
    __compartment: EnterExitCompartment,
    __next_compartment: Option<EnterExitCompartment>,
    _context_stack: Vec<EnterExitFrameContext>,
    log: Vec<String>,
}

impl EnterExit {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            log: Vec::new(),
            __compartment: EnterExitCompartment::new("Off"),
            __next_compartment: None,
        };
let __frame_event = EnterExitFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: EnterExitFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = EnterExitFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = EnterExitFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = EnterExitFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &EnterExitFrameEvent) {
match self.__compartment.state.as_str() {
    "Off" => self._state_Off(__e),
    "On" => self._state_On(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: EnterExitCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Off" => EnterExitStateContext::Off,
    "On" => EnterExitStateContext::On,
    _ => EnterExitStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = EnterExitFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    EnterExitStateContext::Off => {}
    EnterExitStateContext::On => {}
    EnterExitStateContext::Empty => {}
}
    }

    pub fn toggle(&mut self) {
let mut __e = EnterExitFrameEvent::new("toggle");
let __ctx = EnterExitFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Off" => { self._s_Off_toggle(&__e); }
            "On" => { self._s_On_toggle(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = EnterExitFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = EnterExitFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = EnterExitFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
self._context_stack.pop();
    }

    pub fn get_log(&mut self) -> Vec<String> {
let mut __e = EnterExitFrameEvent::new("get_log");
let __ctx = EnterExitFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Off" => { self._s_Off_get_log(&__e); }
            "On" => { self._s_On_get_log(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = EnterExitFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = EnterExitFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = EnterExitFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<Vec<String>>().unwrap()
} else {
    Default::default()
}
    }

    fn _state_Off(&mut self, __e: &EnterExitFrameEvent) {
match __e.message.as_str() {
    "<$" => { self._s_Off_exit(__e); }
    "$>" => { self._s_Off_enter(__e); }
    "get_log" => { self._s_Off_get_log(__e); }
    "toggle" => { self._s_Off_toggle(__e); }
    _ => {}
}
    }

    fn _state_On(&mut self, __e: &EnterExitFrameEvent) {
match __e.message.as_str() {
    "<$" => { self._s_On_exit(__e); }
    "$>" => { self._s_On_enter(__e); }
    "get_log" => { self._s_On_get_log(__e); }
    "toggle" => { self._s_On_toggle(__e); }
    _ => {}
}
    }

    fn _s_Off_exit(&mut self, __e: &EnterExitFrameEvent) {
self.log.push("exit:Off".to_string());
println!("Exiting Off state");
    }

    fn _s_Off_enter(&mut self, __e: &EnterExitFrameEvent) {
self.log.push("enter:Off".to_string());
println!("Entered Off state");
    }

    fn _s_Off_toggle(&mut self, __e: &EnterExitFrameEvent) {
self.__transition(EnterExitCompartment::new("On"));
    }

    fn _s_Off_get_log(&mut self, __e: &EnterExitFrameEvent) {
self.log.clone();
    }

    fn _s_On_get_log(&mut self, __e: &EnterExitFrameEvent) {
self.log.clone();
    }

    fn _s_On_toggle(&mut self, __e: &EnterExitFrameEvent) {
self.__transition(EnterExitCompartment::new("Off"));
    }

    fn _s_On_exit(&mut self, __e: &EnterExitFrameEvent) {
self.log.push("exit:On".to_string());
println!("Exiting On state");
    }

    fn _s_On_enter(&mut self, __e: &EnterExitFrameEvent) {
self.log.push("enter:On".to_string());
println!("Entered On state");
    }
}


fn main() {
    println!("=== Test 05: Enter/Exit Handlers ===");
    let mut s = EnterExit::new();

    // Initial enter should have been called
    let log = s.get_log();
    assert!(log.contains(&"enter:Off".to_string()), "Expected 'enter:Off' in log, got {:?}", log);
    println!("After construction: {:?}", log);

    // Toggle to On - should exit Off, enter On
    s.toggle();
    let log = s.get_log();
    assert!(log.contains(&"exit:Off".to_string()), "Expected 'exit:Off' in log, got {:?}", log);
    assert!(log.contains(&"enter:On".to_string()), "Expected 'enter:On' in log, got {:?}", log);
    println!("After toggle to On: {:?}", log);

    // Toggle back to Off - should exit On, enter Off
    s.toggle();
    let log = s.get_log();
    let enter_off_count = log.iter().filter(|s| *s == "enter:Off").count();
    assert_eq!(enter_off_count, 2, "Expected 2 'enter:Off' entries, got {:?}", log);
    assert!(log.contains(&"exit:On".to_string()), "Expected 'exit:On' in log, got {:?}", log);
    println!("After toggle to Off: {:?}", log);

    println!("PASS: Enter/Exit handlers work correctly");
}
