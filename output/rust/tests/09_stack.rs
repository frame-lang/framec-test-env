use std::collections::HashMap;

struct StackOpsFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl Clone for StackOpsFrameEvent {
    fn clone(&self) -> Self {
        Self {
            message: self.message.clone(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

impl StackOpsFrameEvent {
    fn new(message: &str) -> Self {
        Self {
            message: message.to_string(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

struct StackOpsFrameContext {
    event: StackOpsFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl StackOpsFrameContext {
    fn new(event: StackOpsFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct StackOpsCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<StackOpsFrameEvent>,
}

impl StackOpsCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum StackOpsStateContext {
    Main,
    Sub,
    Empty,
}

impl Default for StackOpsStateContext {
    fn default() -> Self {
        StackOpsStateContext::Main
    }
}

pub struct StackOps {
    _state_stack: Vec<(String, StackOpsStateContext)>,
    __compartment: StackOpsCompartment,
    __next_compartment: Option<StackOpsCompartment>,
    _context_stack: Vec<StackOpsFrameContext>,
}

impl StackOps {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            __compartment: StackOpsCompartment::new("Main"),
            __next_compartment: None,
        };
let __frame_event = StackOpsFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: StackOpsFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = StackOpsFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = StackOpsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = StackOpsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &StackOpsFrameEvent) {
match self.__compartment.state.as_str() {
    "Main" => self._state_Main(__e),
    "Sub" => self._state_Sub(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: StackOpsCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Main" => StackOpsStateContext::Main,
    "Sub" => StackOpsStateContext::Sub,
    _ => StackOpsStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = StackOpsFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    StackOpsStateContext::Main => {}
    StackOpsStateContext::Sub => {}
    StackOpsStateContext::Empty => {}
}
    }

    pub fn push_and_go(&mut self) {
let mut __e = StackOpsFrameEvent::new("push_and_go");
let __ctx = StackOpsFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Main" => { self._s_Main_push_and_go(&__e); }
            "Sub" => { self._s_Sub_push_and_go(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = StackOpsFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = StackOpsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = StackOpsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
self._context_stack.pop();
    }

    pub fn pop_back(&mut self) {
let mut __e = StackOpsFrameEvent::new("pop_back");
let __ctx = StackOpsFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Main" => { self._s_Main_pop_back(&__e); }
            "Sub" => { self._s_Sub_pop_back(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = StackOpsFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = StackOpsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = StackOpsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
self._context_stack.pop();
    }

    pub fn do_work(&mut self) -> String {
let mut __e = StackOpsFrameEvent::new("do_work");
let __ctx = StackOpsFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Main" => { self._s_Main_do_work(&__e); }
            "Sub" => { self._s_Sub_do_work(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = StackOpsFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = StackOpsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = StackOpsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<String>().unwrap()
} else {
    Default::default()
}
    }

    pub fn get_state(&mut self) -> String {
let mut __e = StackOpsFrameEvent::new("get_state");
let __ctx = StackOpsFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Main" => { self._s_Main_get_state(&__e); }
            "Sub" => { self._s_Sub_get_state(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = StackOpsFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = StackOpsFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = StackOpsFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<String>().unwrap()
} else {
    Default::default()
}
    }

    fn _state_Sub(&mut self, __e: &StackOpsFrameEvent) {
match __e.message.as_str() {
    "do_work" => { self._s_Sub_do_work(__e); }
    "get_state" => { self._s_Sub_get_state(__e); }
    "pop_back" => { self._s_Sub_pop_back(__e); }
    "push_and_go" => { self._s_Sub_push_and_go(__e); }
    _ => {}
}
    }

    fn _state_Main(&mut self, __e: &StackOpsFrameEvent) {
match __e.message.as_str() {
    "do_work" => { self._s_Main_do_work(__e); }
    "get_state" => { self._s_Main_get_state(__e); }
    "pop_back" => { self._s_Main_pop_back(__e); }
    "push_and_go" => { self._s_Main_push_and_go(__e); }
    _ => {}
}
    }

    fn _s_Sub_pop_back(&mut self, __e: &StackOpsFrameEvent) {
println!("Popping back to previous state");
self._state_stack_pop();
return;
    }

    fn _s_Sub_do_work(&mut self, __e: &StackOpsFrameEvent) {
"Working in Sub".to_string();
    }

    fn _s_Sub_push_and_go(&mut self, __e: &StackOpsFrameEvent) {
println!("Already in Sub");
    }

    fn _s_Sub_get_state(&mut self, __e: &StackOpsFrameEvent) {
"Sub".to_string();
    }

    fn _s_Main_get_state(&mut self, __e: &StackOpsFrameEvent) {
"Main".to_string();
    }

    fn _s_Main_pop_back(&mut self, __e: &StackOpsFrameEvent) {
println!("Cannot pop - nothing on stack in Main");
    }

    fn _s_Main_push_and_go(&mut self, __e: &StackOpsFrameEvent) {
println!("Pushing Main to stack, going to Sub");
self._state_stack_push();
self.__transition(StackOpsCompartment::new("Sub"));
    }

    fn _s_Main_do_work(&mut self, __e: &StackOpsFrameEvent) {
"Working in Main".to_string();
    }
}


fn main() {
    println!("=== Test 09: Stack Push/Pop ===");
    let mut s = StackOps::new();

    // Initial state should be Main
    let state = s.get_state();
    assert_eq!(state, "Main", "Expected 'Main', got '{}'", state);
    println!("Initial state: {}", state);

    // Do work in Main
    let work = s.do_work();
    assert_eq!(work, "Working in Main", "Expected 'Working in Main', got '{}'", work);
    println!("do_work(): {}", work);

    // Push and go to Sub
    s.push_and_go();
    let state = s.get_state();
    assert_eq!(state, "Sub", "Expected 'Sub', got '{}'", state);
    println!("After push_and_go(): {}", state);

    // Do work in Sub
    let work = s.do_work();
    assert_eq!(work, "Working in Sub", "Expected 'Working in Sub', got '{}'", work);
    println!("do_work(): {}", work);

    // Pop back to Main
    s.pop_back();
    let state = s.get_state();
    assert_eq!(state, "Main", "Expected 'Main' after pop, got '{}'", state);
    println!("After pop_back(): {}", state);

    println!("PASS: Stack push/pop works correctly");
}
