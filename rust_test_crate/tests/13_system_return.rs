use std::collections::HashMap;

#[derive(Clone, Debug)]
struct SystemReturnTestFrameEvent {
    message: String,
}

impl SystemReturnTestFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct SystemReturnTestCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<SystemReturnTestFrameEvent>,
}

impl SystemReturnTestCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone, Default)]
struct CalculatorContext {
    value: i32,
}

#[derive(Clone)]
enum SystemReturnTestStateContext {
    Calculator(CalculatorContext),
    Empty,
}

impl Default for SystemReturnTestStateContext {
    fn default() -> Self {
        SystemReturnTestStateContext::Calculator(CalculatorContext::default())
    }
}

pub struct SystemReturnTest {
    _state_stack: Vec<(String, SystemReturnTestStateContext)>,
    __compartment: SystemReturnTestCompartment,
    __next_compartment: Option<SystemReturnTestCompartment>,
    _sv_value: i32,
}

impl SystemReturnTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _sv_value: 0,
            __compartment: SystemReturnTestCompartment::new("Calculator"),
            __next_compartment: None,
        };
let __frame_event = SystemReturnTestFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: SystemReturnTestFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = SystemReturnTestFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = SystemReturnTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = SystemReturnTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &SystemReturnTestFrameEvent) {
match self.__compartment.state.as_str() {
    "Calculator" => self._state_Calculator(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: SystemReturnTestCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Calculator" => SystemReturnTestStateContext::Calculator(CalculatorContext { value: self._sv_value }),
    _ => SystemReturnTestStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = SystemReturnTestFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    SystemReturnTestStateContext::Calculator(ctx) => {
        self._sv_value = ctx.value;
    }
    SystemReturnTestStateContext::Empty => {}
}
    }

    pub fn add(&mut self, a: i32, b: i32) -> i32 {
let __e = SystemReturnTestFrameEvent::new("add");
match self.__compartment.state.as_str() {
            "Calculator" => self._s_Calculator_add(&__e, a, b),
            _ => Default::default(),
        }
    }

    pub fn multiply(&mut self, a: i32, b: i32) -> i32 {
let __e = SystemReturnTestFrameEvent::new("multiply");
match self.__compartment.state.as_str() {
            "Calculator" => self._s_Calculator_multiply(&__e, a, b),
            _ => Default::default(),
        }
    }

    pub fn get_value(&mut self) -> i32 {
let __e = SystemReturnTestFrameEvent::new("get_value");
match self.__compartment.state.as_str() {
            "Calculator" => self._s_Calculator_get_value(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Calculator(&mut self, __e: &SystemReturnTestFrameEvent) {
match __e.message.as_str() {
    "get_value" => { self._s_Calculator_get_value(__e); }
    "$>" => {
        self._sv_value = 0;
    }
    _ => {}
}
    }

    fn _s_Calculator_add(&mut self, __e: &SystemReturnTestFrameEvent, a: i32, b: i32) -> i32 {
return a + b
    }

    fn _s_Calculator_get_value(&mut self, __e: &SystemReturnTestFrameEvent) -> i32 {
self._sv_value = 42;
return self._sv_value
    }

    fn _s_Calculator_multiply(&mut self, __e: &SystemReturnTestFrameEvent, a: i32, b: i32) -> i32 {
return a * b
    }
}


fn main() {
    println!("=== Test 13: System Return ===");
    let mut calc = SystemReturnTest::new();

    // Test caret return sugar
    let result = calc.add(3, 5);
    assert_eq!(result, 8, "Expected 8, got {}", result);
    println!("add(3, 5) = {}", result);

    // Test system.return = expr
    let result = calc.multiply(4, 7);
    assert_eq!(result, 28, "Expected 28, got {}", result);
    println!("multiply(4, 7) = {}", result);

    // Test return with state variable
    let value = calc.get_value();
    assert_eq!(value, 42, "Expected 42, got {}", value);
    println!("get_value() = {}", value);

    println!("PASS: System return works correctly");
}
