use std::collections::HashMap;

#[derive(Clone, Default)]
struct CounterContext {
    count: i32,
}

#[derive(Clone)]
enum StateVarBasicCompartment {
    Counter(CounterContext),
    Empty,
}

impl Default for StateVarBasicCompartment {
    fn default() -> Self {
        StateVarBasicCompartment::Counter(CounterContext::default())
    }
}

pub struct StateVarBasic {
    _state: String,
    _state_stack: Vec<(String, StateVarBasicCompartment)>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    _sv_count: i32,
}

impl StateVarBasic {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            _sv_count: 0,
            _state: String::from("Counter"),
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
    "Counter" => {
        self._sv_count = 0;
    }
    _ => {}
}
    }

    fn _exit(&mut self) {
        // No exit handlers
    }

    fn _state_stack_push(&mut self) {
let compartment = match self._state.as_str() {
    "Counter" => StateVarBasicCompartment::Counter(CounterContext { count: self._sv_count }),
    _ => StateVarBasicCompartment::Empty,
};
self._state_stack.push((self._state.clone(), compartment));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, compartment) = self._state_stack.pop().unwrap();
self._exit();
self._state = saved_state;
match compartment {
    StateVarBasicCompartment::Counter(ctx) => {
        self._sv_count = ctx.count;
    }
    StateVarBasicCompartment::Empty => {}
}
    }

    pub fn increment(&mut self) -> i32 {
match self._state.as_str() {
            "Counter" => self._s_Counter_increment(),
            _ => Default::default(),
        }
    }

    pub fn get_count(&mut self) -> i32 {
match self._state.as_str() {
            "Counter" => self._s_Counter_get_count(),
            _ => Default::default(),
        }
    }

    pub fn reset(&mut self) {
match self._state.as_str() {
            "Counter" => { self._s_Counter_reset(); }
            _ => {}
        }
    }

    fn _s_Counter_get_count(&mut self) -> i32 {
self._sv_count
    }

    fn _s_Counter_increment(&mut self) -> i32 {
self._sv_count = self._sv_count + 1;
self._sv_count
    }

    fn _s_Counter_reset(&mut self) {
self._sv_count = 0;
    }
}


fn main() {
    println!("=== Test 10: State Variable Basic ===");
    let mut s = StateVarBasic::new();

    // Initial value should be 0
    let count = s.get_count();
    assert_eq!(count, 0, "Expected 0, got {}", count);
    println!("Initial count: {}", count);

    // Increment should return new value
    let result = s.increment();
    assert_eq!(result, 1, "Expected 1 after first increment, got {}", result);
    println!("After first increment: {}", result);

    // Second increment
    let result = s.increment();
    assert_eq!(result, 2, "Expected 2 after second increment, got {}", result);
    println!("After second increment: {}", result);

    // Reset should set back to 0
    s.reset();
    let count = s.get_count();
    assert_eq!(count, 0, "Expected 0 after reset, got {}", count);
    println!("After reset: {}", count);

    println!("PASS: State variable basic operations work correctly");
}
