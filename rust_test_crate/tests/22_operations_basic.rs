use std::collections::HashMap;

#[derive(Clone, Debug)]
struct OperationsTestFrameEvent {
    message: String,
}

impl OperationsTestFrameEvent {
    fn new(message: &str) -> Self {
        Self { message: message.to_string() }
    }
}

#[derive(Clone)]
struct OperationsTestCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<OperationsTestFrameEvent>,
}

impl OperationsTestCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum OperationsTestStateContext {
    Ready,
    Empty,
}

impl Default for OperationsTestStateContext {
    fn default() -> Self {
        OperationsTestStateContext::Ready
    }
}

pub struct OperationsTest {
    _state_stack: Vec<(String, OperationsTestStateContext)>,
    __compartment: OperationsTestCompartment,
    __next_compartment: Option<OperationsTestCompartment>,
    last_result: i32,
}

impl OperationsTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            last_result: 0,
            __compartment: OperationsTestCompartment::new("Ready"),
            __next_compartment: None,
        };
let __frame_event = OperationsTestFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: OperationsTestFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = OperationsTestFrameEvent::new("$<");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = OperationsTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = OperationsTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &OperationsTestFrameEvent) {
match self.__compartment.state.as_str() {
    "Ready" => self._state_Ready(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: OperationsTestCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Ready" => OperationsTestStateContext::Ready,
    _ => OperationsTestStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = OperationsTestFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    OperationsTestStateContext::Ready => {}
    OperationsTestStateContext::Empty => {}
}
    }

    pub fn compute(&mut self, a: i32, b: i32) -> i32 {
let __e = OperationsTestFrameEvent::new("compute");
match self.__compartment.state.as_str() {
            "Ready" => self._s_Ready_compute(&__e, a, b),
            _ => Default::default(),
        }
    }

    pub fn get_last_result(&mut self) -> i32 {
let __e = OperationsTestFrameEvent::new("get_last_result");
match self.__compartment.state.as_str() {
            "Ready" => self._s_Ready_get_last_result(&__e),
            _ => Default::default(),
        }
    }

    fn _state_Ready(&mut self, __e: &OperationsTestFrameEvent) {
match __e.message.as_str() {
    "get_last_result" => { self._s_Ready_get_last_result(__e); }
    _ => {}
}
    }

    fn _s_Ready_get_last_result(&mut self, __e: &OperationsTestFrameEvent) -> i32 {
return self.last_result;
    }

    fn _s_Ready_compute(&mut self, __e: &OperationsTestFrameEvent, a: i32, b: i32) -> i32 {
// Use instance operations
let sum_val = self.add(a, b);
let prod_val = self.multiply(a, b);
let last_result = sum_val + prod_val;
return last_result;
    }

    pub fn add(&mut self, x: i32, y: i32) -> i32 {
            return x + y;
    }

    pub fn multiply(&mut self, x: i32, y: i32) -> i32 {
            return x * y;
    }

    pub fn factorial(n: i32) -> i32 {
            if n <= 1 {
                return 1;
            }
            return n * OperationsTest::factorial(n - 1);
    }

    pub fn is_even(n: i32) -> bool {
            return n % 2 == 0;
    }
}


fn main() {
    println!("=== Test 22: Operations Basic (Rust) ===");
    let mut s = OperationsTest::new();

    // Test 1: Instance operations
    let mut result = s.add(3, 4);
    assert_eq!(result, 7, "Expected 7, got {}", result);
    println!("1. add(3, 4) = {}", result);

    result = s.multiply(3, 4);
    assert_eq!(result, 12, "Expected 12, got {}", result);
    println!("2. multiply(3, 4) = {}", result);

    // Test 2: Operations used in handler
    result = s.compute(3, 4);
    // compute returns add(3,4) + multiply(3,4) = 7 + 12 = 19
    assert_eq!(result, 19, "Expected 19, got {}", result);
    println!("3. compute(3, 4) = {}", result);

    // Test 3: Static operations
    result = OperationsTest::factorial(5);
    assert_eq!(result, 120, "Expected 120, got {}", result);
    println!("4. factorial(5) = {}", result);

    let mut is_even = OperationsTest::is_even(4);
    assert_eq!(is_even, true, "Expected true, got {}", is_even);
    println!("5. is_even(4) = {}", is_even);

    is_even = OperationsTest::is_even(7);
    assert_eq!(is_even, false, "Expected false, got {}", is_even);
    println!("6. is_even(7) = {}", is_even);

    // Test 4: Static can also be called on instance (via type)
    result = OperationsTest::factorial(4);
    assert_eq!(result, 24, "Expected 24, got {}", result);
    println!("7. OperationsTest::factorial(4) = {}", result);

    println!("PASS: Operations basic works correctly");
}
