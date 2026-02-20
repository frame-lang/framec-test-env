use std::collections::HashMap;

pub struct StackOps {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
}

impl StackOps {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            _state: String::from("Main"),
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

    pub fn push_and_go(&mut self) {
match self._state.as_str() {
            "Main" => { self._s_Main_push_and_go(); }
            "Sub" => { self._s_Sub_push_and_go(); }
            _ => {}
        }
    }

    pub fn pop_back(&mut self) {
match self._state.as_str() {
            "Main" => { self._s_Main_pop_back(); }
            "Sub" => { self._s_Sub_pop_back(); }
            _ => {}
        }
    }

    pub fn do_work(&mut self) -> String {
match self._state.as_str() {
            "Main" => self._s_Main_do_work(),
            "Sub" => self._s_Sub_do_work(),
            _ => Default::default(),
        }
    }

    pub fn get_state(&mut self) -> String {
match self._state.as_str() {
            "Main" => self._s_Main_get_state(),
            "Sub" => self._s_Sub_get_state(),
            _ => Default::default(),
        }
    }

    fn _s_Sub_push_and_go(&mut self) {
println!("Already in Sub");
    }

    fn _s_Sub_pop_back(&mut self) {
println!("Popping back to previous state");
let __popped_state = *self._state_stack.pop().unwrap().downcast::<String>().unwrap();
self._transition(&__popped_state);
return;
    }

    fn _s_Sub_do_work(&mut self) -> String {
"Working in Sub".to_string()
    }

    fn _s_Sub_get_state(&mut self) -> String {
"Sub".to_string()
    }

    fn _s_Main_pop_back(&mut self) {
println!("Cannot pop - nothing on stack in Main");
    }

    fn _s_Main_do_work(&mut self) -> String {
"Working in Main".to_string()
    }

    fn _s_Main_push_and_go(&mut self) {
println!("Pushing Main to stack, going to Sub");
self._state_stack.push(Box::new(self._state.clone()));
self._transition("Sub");
    }

    fn _s_Main_get_state(&mut self) -> String {
"Main".to_string()
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
