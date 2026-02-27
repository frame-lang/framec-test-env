
// =============================================================================
// Test 01: Interface Return
// =============================================================================
// Validates that event handler returns work correctly via the context stack.
// Tests both syntaxes:
//   - return value     (sugar - expands to @@:return = value)
//   - @@:return = value (explicit context assignment)
// =============================================================================


use std::collections::HashMap;

struct InterfaceReturnFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl Clone for InterfaceReturnFrameEvent {
    fn clone(&self) -> Self {
        Self {
            message: self.message.clone(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

impl InterfaceReturnFrameEvent {
    fn new(message: &str) -> Self {
        Self {
            message: message.to_string(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

struct InterfaceReturnFrameContext {
    event: InterfaceReturnFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl InterfaceReturnFrameContext {
    fn new(event: InterfaceReturnFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct InterfaceReturnCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<InterfaceReturnFrameEvent>,
}

impl InterfaceReturnCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum InterfaceReturnStateContext {
    Active,
    Empty,
}

impl Default for InterfaceReturnStateContext {
    fn default() -> Self {
        InterfaceReturnStateContext::Active
    }
}

pub struct InterfaceReturn {
    _state_stack: Vec<(String, InterfaceReturnStateContext)>,
    __compartment: InterfaceReturnCompartment,
    __next_compartment: Option<InterfaceReturnCompartment>,
    _context_stack: Vec<InterfaceReturnFrameContext>,
}

impl InterfaceReturn {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            __compartment: InterfaceReturnCompartment::new("Active"),
            __next_compartment: None,
        };
let __frame_event = InterfaceReturnFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: InterfaceReturnFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = InterfaceReturnFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = InterfaceReturnFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = InterfaceReturnFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &InterfaceReturnFrameEvent) {
match self.__compartment.state.as_str() {
    "Active" => self._state_Active(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: InterfaceReturnCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Active" => InterfaceReturnStateContext::Active,
    _ => InterfaceReturnStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = InterfaceReturnFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    InterfaceReturnStateContext::Active => {}
    InterfaceReturnStateContext::Empty => {}
}
    }

    pub fn bool_return(&mut self) -> bool {
let mut __e = InterfaceReturnFrameEvent::new("bool_return");
let __ctx = InterfaceReturnFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Active" => { self._s_Active_bool_return(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = InterfaceReturnFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = InterfaceReturnFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = InterfaceReturnFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<bool>().unwrap()
} else {
    Default::default()
}
    }

    pub fn int_return(&mut self) -> i32 {
let mut __e = InterfaceReturnFrameEvent::new("int_return");
let __ctx = InterfaceReturnFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Active" => { self._s_Active_int_return(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = InterfaceReturnFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = InterfaceReturnFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = InterfaceReturnFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<i32>().unwrap()
} else {
    Default::default()
}
    }

    pub fn string_return(&mut self) -> String {
let mut __e = InterfaceReturnFrameEvent::new("string_return");
let __ctx = InterfaceReturnFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Active" => { self._s_Active_string_return(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = InterfaceReturnFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = InterfaceReturnFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = InterfaceReturnFrameEvent::new("$>");
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

    pub fn conditional_return(&mut self, x: i32) -> String {
let mut __e = InterfaceReturnFrameEvent::new("conditional_return");
__e.parameters.insert("x".to_string(), Box::new(x) as Box<dyn std::any::Any>);
let __ctx = InterfaceReturnFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Active" => { self._s_Active_conditional_return(&__e, x); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = InterfaceReturnFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = InterfaceReturnFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = InterfaceReturnFrameEvent::new("$>");
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

    pub fn computed_return(&mut self, a: i32, b: i32) -> i32 {
let mut __e = InterfaceReturnFrameEvent::new("computed_return");
__e.parameters.insert("a".to_string(), Box::new(a) as Box<dyn std::any::Any>);
__e.parameters.insert("b".to_string(), Box::new(b) as Box<dyn std::any::Any>);
let __ctx = InterfaceReturnFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Active" => { self._s_Active_computed_return(&__e, a, b); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = InterfaceReturnFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = InterfaceReturnFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = InterfaceReturnFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<i32>().unwrap()
} else {
    Default::default()
}
    }

    pub fn explicit_bool(&mut self) -> bool {
let mut __e = InterfaceReturnFrameEvent::new("explicit_bool");
let __ctx = InterfaceReturnFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Active" => { self._s_Active_explicit_bool(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = InterfaceReturnFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = InterfaceReturnFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = InterfaceReturnFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<bool>().unwrap()
} else {
    Default::default()
}
    }

    pub fn explicit_int(&mut self) -> i32 {
let mut __e = InterfaceReturnFrameEvent::new("explicit_int");
let __ctx = InterfaceReturnFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Active" => { self._s_Active_explicit_int(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = InterfaceReturnFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = InterfaceReturnFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = InterfaceReturnFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<i32>().unwrap()
} else {
    Default::default()
}
    }

    pub fn explicit_string(&mut self) -> String {
let mut __e = InterfaceReturnFrameEvent::new("explicit_string");
let __ctx = InterfaceReturnFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Active" => { self._s_Active_explicit_string(&__e); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = InterfaceReturnFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = InterfaceReturnFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = InterfaceReturnFrameEvent::new("$>");
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

    pub fn explicit_conditional(&mut self, x: i32) -> String {
let mut __e = InterfaceReturnFrameEvent::new("explicit_conditional");
__e.parameters.insert("x".to_string(), Box::new(x) as Box<dyn std::any::Any>);
let __ctx = InterfaceReturnFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Active" => { self._s_Active_explicit_conditional(&__e, x); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = InterfaceReturnFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = InterfaceReturnFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = InterfaceReturnFrameEvent::new("$>");
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

    pub fn explicit_computed(&mut self, a: i32, b: i32) -> i32 {
let mut __e = InterfaceReturnFrameEvent::new("explicit_computed");
__e.parameters.insert("a".to_string(), Box::new(a) as Box<dyn std::any::Any>);
__e.parameters.insert("b".to_string(), Box::new(b) as Box<dyn std::any::Any>);
let __ctx = InterfaceReturnFrameContext::new(__e.clone(), None);
self._context_stack.push(__ctx);
match self.__compartment.state.as_str() {
            "Active" => { self._s_Active_explicit_computed(&__e, a, b); }
            _ => {}
        }
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    let exit_event = InterfaceReturnFrameEvent::new("<$");
    self.__router(&exit_event);
    self.__compartment = next_compartment;
    if self.__compartment.forward_event.is_none() {
        let enter_event = InterfaceReturnFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            self.__router(&forward_event);
        } else {
            let enter_event = InterfaceReturnFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
let __ctx = self._context_stack.pop().unwrap();
if let Some(ret) = __ctx._return {
    *ret.downcast::<i32>().unwrap()
} else {
    Default::default()
}
    }

    fn _state_Active(&mut self, __e: &InterfaceReturnFrameEvent) {
match __e.message.as_str() {
    "bool_return" => { self._s_Active_bool_return(__e); }
    "explicit_bool" => { self._s_Active_explicit_bool(__e); }
    "explicit_int" => { self._s_Active_explicit_int(__e); }
    "explicit_string" => { self._s_Active_explicit_string(__e); }
    "int_return" => { self._s_Active_int_return(__e); }
    "string_return" => { self._s_Active_string_return(__e); }
    _ => {}
}
    }

    fn _s_Active_explicit_bool(&mut self, __e: &InterfaceReturnFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(true)); }
    }

    fn _s_Active_explicit_string(&mut self, __e: &InterfaceReturnFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new("Frame".to_string())); }
    }

    fn _s_Active_explicit_computed(&mut self, __e: &InterfaceReturnFrameEvent, a: i32, b: i32) {
let result = a * b + 10;
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(result)); }
    }

    fn _s_Active_string_return(&mut self, __e: &InterfaceReturnFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new("Frame".to_string())); }
return;
    }

    fn _s_Active_explicit_conditional(&mut self, __e: &InterfaceReturnFrameEvent, x: i32) {
if x < 0 {
    if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new("negative".to_string())); }
    return
} else if x == 0 {
    if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new("zero".to_string())); }
    return
} else {
    if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new("positive".to_string())); }
}
    }

    fn _s_Active_int_return(&mut self, __e: &InterfaceReturnFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(42)); }
return;
    }

    fn _s_Active_bool_return(&mut self, __e: &InterfaceReturnFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(true)); }
return;
    }

    fn _s_Active_conditional_return(&mut self, __e: &InterfaceReturnFrameEvent, x: i32) {
if x < 0 {
    if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new("negative".to_string())); }
    return;
} else if x == 0 {
    if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new("zero".to_string())); }
    return;
} else {
    if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new("positive".to_string())); }
    return;
}
    }

    fn _s_Active_explicit_int(&mut self, __e: &InterfaceReturnFrameEvent) {
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(42)); }
    }

    fn _s_Active_computed_return(&mut self, __e: &InterfaceReturnFrameEvent, a: i32, b: i32) {
let result = a * b + 10;
if let Some(ctx) = self._context_stack.last_mut() { ctx._return = Some(Box::new(result)); }
return;
    }
}


fn main() {
    println!("=== Test 01: Interface Return (Rust) ===");
    let mut s = InterfaceReturn::new();
    let mut errors: Vec<String> = Vec::new();

    println!("-- Testing 'return value' sugar --");

    let r = s.bool_return();
    if r != true {
        errors.push(format!("bool_return: expected true, got {}", r));
    } else {
        println!("1. bool_return() = {}", r);
    }

    let r = s.int_return();
    if r != 42 {
        errors.push(format!("int_return: expected 42, got {}", r));
    } else {
        println!("2. int_return() = {}", r);
    }

    let r = s.string_return();
    if r != "Frame" {
        errors.push(format!("string_return: expected 'Frame', got '{}'", r));
    } else {
        println!("3. string_return() = '{}'", r);
    }

    let r = s.conditional_return(-5);
    if r != "negative" {
        errors.push(format!("conditional_return(-5): expected 'negative', got '{}'", r));
    }
    let r = s.conditional_return(0);
    if r != "zero" {
        errors.push(format!("conditional_return(0): expected 'zero', got '{}'", r));
    }
    let r = s.conditional_return(10);
    if r != "positive" {
        errors.push(format!("conditional_return(10): expected 'positive', got '{}'", r));
    } else {
        println!("4. conditional_return(-5,0,10) = 'negative','zero','positive'");
    }

    let r = s.computed_return(3, 4);
    if r != 22 {
        errors.push(format!("computed_return(3,4): expected 22, got {}", r));
    } else {
        println!("5. computed_return(3,4) = {}", r);
    }

    println!("-- Testing '@@:return = value' explicit --");

    let r = s.explicit_bool();
    if r != true {
        errors.push(format!("explicit_bool: expected true, got {}", r));
    } else {
        println!("6. explicit_bool() = {}", r);
    }

    let r = s.explicit_int();
    if r != 42 {
        errors.push(format!("explicit_int: expected 42, got {}", r));
    } else {
        println!("7. explicit_int() = {}", r);
    }

    let r = s.explicit_string();
    if r != "Frame" {
        errors.push(format!("explicit_string: expected 'Frame', got '{}'", r));
    } else {
        println!("8. explicit_string() = '{}'", r);
    }

    let r = s.explicit_conditional(-5);
    if r != "negative" {
        errors.push(format!("explicit_conditional(-5): expected 'negative', got '{}'", r));
    }
    let r = s.explicit_conditional(0);
    if r != "zero" {
        errors.push(format!("explicit_conditional(0): expected 'zero', got '{}'", r));
    }
    let r = s.explicit_conditional(10);
    if r != "positive" {
        errors.push(format!("explicit_conditional(10): expected 'positive', got '{}'", r));
    } else {
        println!("9. explicit_conditional(-5,0,10) = 'negative','zero','positive'");
    }

    let r = s.explicit_computed(3, 4);
    if r != 22 {
        errors.push(format!("explicit_computed(3,4): expected 22, got {}", r));
    } else {
        println!("10. explicit_computed(3,4) = {}", r);
    }

    if !errors.is_empty() {
        for e in &errors {
            println!("FAIL: {}", e);
        }
        panic!("{} test(s) failed", errors.len());
    } else {
        println!("PASS: All interface return tests passed");
    }
}
