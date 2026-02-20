use std::collections::HashMap;

#[derive(Clone, Default)]
struct CounterContext {
    count: i32,
}

#[derive(Clone)]
enum StateVarReentryCompartment {
    Counter(CounterContext),
    Other,
    Empty,
}

impl Default for StateVarReentryCompartment {
    fn default() -> Self {
        StateVarReentryCompartment::Counter(CounterContext::default())
    }
}

pub struct StateVarReentry {
    _state: String,
    _state_stack: Vec<(String, StateVarReentryCompartment)>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    _sv_count: i32,
}

impl StateVarReentry {
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
    "Counter" => StateVarReentryCompartment::Counter(CounterContext { count: self._sv_count }),
    "Other" => StateVarReentryCompartment::Other,
    _ => StateVarReentryCompartment::Empty,
};
self._state_stack.push((self._state.clone(), compartment));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, compartment) = self._state_stack.pop().unwrap();
self._exit();
self._state = saved_state;
match compartment {
    StateVarReentryCompartment::Counter(ctx) => {
        self._sv_count = ctx.count;
    }
    StateVarReentryCompartment::Other => {}
    StateVarReentryCompartment::Empty => {}
}
    }

    pub fn increment(&mut self) -> i32 {
match self._state.as_str() {
            "Counter" => self._s_Counter_increment(),
            "Other" => self._s_Other_increment(),
            _ => Default::default(),
        }
    }

    pub fn get_count(&mut self) -> i32 {
match self._state.as_str() {
            "Counter" => self._s_Counter_get_count(),
            "Other" => self._s_Other_get_count(),
            _ => Default::default(),
        }
    }

    pub fn go_other(&mut self) {
match self._state.as_str() {
            "Counter" => { self._s_Counter_go_other(); }
            _ => {}
        }
    }

    pub fn come_back(&mut self) {
match self._state.as_str() {
            "Other" => { self._s_Other_come_back(); }
            _ => {}
        }
    }

    fn _s_Counter_increment(&mut self) -> i32 {
self._sv_count = self._sv_count + 1;
self._sv_count
    }

    fn _s_Counter_get_count(&mut self) -> i32 {
self._sv_count
    }

    fn _s_Counter_go_other(&mut self) {
self._transition("Other");
    }

    fn _s_Other_come_back(&mut self) {
self._transition("Counter");
    }

    fn _s_Other_get_count(&mut self) -> i32 {
-1
    }

    fn _s_Other_increment(&mut self) -> i32 {
-1
    }
}


fn main() {
    println!("=== Test 11: State Variable Reentry ===");
    let mut s = StateVarReentry::new();

    // Increment a few times
    s.increment();
    s.increment();
    let count = s.get_count();
    assert_eq!(count, 2, "Expected 2 after two increments, got {}", count);
    println!("Count before leaving: {}", count);

    // Leave the state
    s.go_other();
    println!("Transitioned to Other state");

    // Come back - state var should be reinitialized to 0
    s.come_back();
    let count = s.get_count();
    assert_eq!(count, 0, "Expected 0 after re-entering Counter (state var reinit), got {}", count);
    println!("Count after re-entering Counter: {}", count);

    // Increment again to verify it works
    let result = s.increment();
    assert_eq!(result, 1, "Expected 1 after increment, got {}", result);
    println!("After increment: {}", result);

    println!("PASS: State variables reinitialize on state reentry");
}
