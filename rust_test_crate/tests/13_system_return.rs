use std::collections::HashMap;

#[derive(Clone, Default)]
struct CalculatorContext {
    value: i32,
}

#[derive(Clone)]
enum SystemReturnTestCompartment {
    Calculator(CalculatorContext),
    Empty,
}

impl Default for SystemReturnTestCompartment {
    fn default() -> Self {
        SystemReturnTestCompartment::Calculator(CalculatorContext::default())
    }
}

pub struct SystemReturnTest {
    _state: String,
    _state_stack: Vec<(String, SystemReturnTestCompartment)>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    _sv_value: i32,
}

impl SystemReturnTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            _sv_value: 0,
            _state: String::from("Calculator"),
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
match self._state.as_str() {
    "Calculator" => {
        self._sv_value = 0;
    }
    _ => {}
}
    }

    fn _exit(&mut self) {
        // No exit handlers
    }

    fn _state_stack_push(&mut self) {
let compartment = match self._state.as_str() {
    "Calculator" => SystemReturnTestCompartment::Calculator(CalculatorContext { value: self._sv_value }),
    _ => SystemReturnTestCompartment::Empty,
};
self._state_stack.push((self._state.clone(), compartment));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, compartment) = self._state_stack.pop().unwrap();
self._exit();
self._state = saved_state;
match compartment {
    SystemReturnTestCompartment::Calculator(ctx) => {
        self._sv_value = ctx.value;
    }
    SystemReturnTestCompartment::Empty => {}
}
    }

    pub fn add(&mut self, a: i32, b: i32) -> i32 {
match self._state.as_str() {
            "Calculator" => self._s_Calculator_add(a, b),
            _ => Default::default(),
        }
    }

    pub fn multiply(&mut self, a: i32, b: i32) -> i32 {
match self._state.as_str() {
            "Calculator" => self._s_Calculator_multiply(a, b),
            _ => Default::default(),
        }
    }

    pub fn get_value(&mut self) -> i32 {
match self._state.as_str() {
            "Calculator" => self._s_Calculator_get_value(),
            _ => Default::default(),
        }
    }

    fn _s_Calculator_get_value(&mut self) -> i32 {
self._sv_value = 42;
return self._sv_value
    }

    fn _s_Calculator_add(&mut self, a: i32, b: i32) -> i32 {
return a + b
    }

    fn _s_Calculator_multiply(&mut self, a: i32, b: i32) -> i32 {
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
