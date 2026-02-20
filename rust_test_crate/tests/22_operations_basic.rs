use std::collections::HashMap;

pub struct OperationsTest {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    last_result: i32,
}

impl OperationsTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            last_result: 0,
            _state: String::from("Ready"),
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
        // No enter handlers
    }

    fn _exit(&mut self) {
        // No exit handlers
    }

    pub fn compute(&mut self, a: i32, b: i32) -> i32 {
match self._state.as_str() {
            "Ready" => self._s_Ready_compute(a, b),
            _ => Default::default(),
        }
    }

    pub fn get_last_result(&mut self) -> i32 {
match self._state.as_str() {
            "Ready" => self._s_Ready_get_last_result(),
            _ => Default::default(),
        }
    }

    fn _s_Ready_compute(&mut self, a: i32, b: i32) -> i32 {
// Use instance operations
let sum_val = self.add(a, b);
let prod_val = self.multiply(a, b);
let last_result = sum_val + prod_val;
return last_result;
    }

    fn _s_Ready_get_last_result(&mut self) -> i32 {
return self.last_result;
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
