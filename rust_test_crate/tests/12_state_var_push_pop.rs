
// Rust now preserves state variables across push/pop using typed compartment enum.
// See generate_rust_compartment_types() in system_codegen.rs


use std::collections::HashMap;

#[derive(Clone, Default)]
struct CounterContext {
    count: i32,
}

#[derive(Clone, Default)]
struct OtherContext {
    other_count: i32,
}

#[derive(Clone)]
enum StateVarPushPopCompartment {
    Counter(CounterContext),
    Other(OtherContext),
    Empty,
}

impl Default for StateVarPushPopCompartment {
    fn default() -> Self {
        StateVarPushPopCompartment::Counter(CounterContext::default())
    }
}

pub struct StateVarPushPop {
    _state: String,
    _state_stack: Vec<(String, StateVarPushPopCompartment)>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    _sv_count: i32,
    _sv_other_count: i32,
}

impl StateVarPushPop {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            _sv_count: 0,
            _sv_other_count: 0,
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

    fn _change_state(&mut self, target_state: &str) {
        self._state = target_state.to_string();
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
    "Other" => {
        self._sv_other_count = 100;
    }
    _ => {}
}
    }

    fn _exit(&mut self) {
        // No exit handlers
    }

    fn _state_stack_push(&mut self) {
let compartment = match self._state.as_str() {
    "Counter" => StateVarPushPopCompartment::Counter(CounterContext { count: self._sv_count }),
    "Other" => StateVarPushPopCompartment::Other(OtherContext { other_count: self._sv_other_count }),
    _ => StateVarPushPopCompartment::Empty,
};
self._state_stack.push((self._state.clone(), compartment));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, compartment) = self._state_stack.pop().unwrap();
self._exit();
self._state = saved_state;
match compartment {
    StateVarPushPopCompartment::Counter(ctx) => {
        self._sv_count = ctx.count;
    }
    StateVarPushPopCompartment::Other(ctx) => {
        self._sv_other_count = ctx.other_count;
    }
    StateVarPushPopCompartment::Empty => {}
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

    pub fn save_and_go(&mut self) {
match self._state.as_str() {
            "Counter" => { self._s_Counter_save_and_go(); }
            _ => {}
        }
    }

    pub fn restore(&mut self) {
match self._state.as_str() {
            "Other" => { self._s_Other_restore(); }
            _ => {}
        }
    }

    fn _s_Other_increment(&mut self) -> i32 {
self._sv_other_count = self._sv_other_count + 1;
self._sv_other_count
    }

    fn _s_Other_get_count(&mut self) -> i32 {
self._sv_other_count
    }

    fn _s_Other_restore(&mut self) {
self._state_stack_pop();
return;
    }

    fn _s_Counter_increment(&mut self) -> i32 {
self._sv_count = self._sv_count + 1;
self._sv_count
    }

    fn _s_Counter_get_count(&mut self) -> i32 {
self._sv_count
    }

    fn _s_Counter_save_and_go(&mut self) {
self._state_stack_push();
self._transition("Other");
    }
}


fn main() {
    println!("=== Test 12: State Variable Push/Pop ===");
    let mut s = StateVarPushPop::new();

    // Increment counter to 3
    s.increment();
    s.increment();
    s.increment();
    let count = s.get_count();
    assert_eq!(count, 3, "Expected 3, got {}", count);
    println!("Counter before push: {}", count);

    // Push and go to Other state
    s.save_and_go();
    println!("Pushed and transitioned to Other");

    // In Other state, count should be 100 (Other's state var)
    let count = s.get_count();
    assert_eq!(count, 100, "Expected 100 in Other state, got {}", count);
    println!("Other state count: {}", count);

    // Increment in Other
    s.increment();
    let count = s.get_count();
    assert_eq!(count, 101, "Expected 101 after increment, got {}", count);
    println!("Other state after increment: {}", count);

    // Pop back - state vars are now preserved in Rust (same as Python/TypeScript)
    s.restore();
    println!("Popped back to Counter");

    let count = s.get_count();
    // State vars are preserved across push/pop
    assert_eq!(count, 3, "Expected 3 after pop (preserved), got {}", count);
    println!("Counter after pop: {} (preserved!)", count);

    // Increment to verify it works
    s.increment();
    let count = s.get_count();
    assert_eq!(count, 4, "Expected 4, got {}", count);
    println!("Counter after increment: {}", count);

    println!("PASS: State vars preserved across push/pop");
}

