
// Test: Context Stack Reentrancy
// Validates that nested interface calls maintain separate contexts


use std::collections::HashMap;

#[derive(Clone, Debug)]
struct ContextReentrantTestFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, String>,
}

impl ContextReentrantTestFrameEvent {
    fn new(message: &str) -> Self {
        Self {
            message: message.to_string(),
            parameters: std::collections::HashMap::new(),
        }
    }
    fn with_parameters(message: &str, parameters: std::collections::HashMap<String, String>) -> Self {
        Self { message: message.to_string(), parameters }
    }
}

struct ContextReentrantTestFrameContext {
    event: ContextReentrantTestFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl ContextReentrantTestFrameContext {
    fn new(event: ContextReentrantTestFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
struct ContextReentrantTestCompartment {
    state: String,
    state_vars: std::collections::HashMap<String, i32>,
    forward_event: Option<ContextReentrantTestFrameEvent>,
}

impl ContextReentrantTestCompartment {
    fn new(state: &str) -> Self {
        Self {
            state: state.to_string(),
            state_vars: std::collections::HashMap::new(),
            forward_event: None,
        }
    }
}

#[derive(Clone)]
enum ContextReentrantTestStateContext {
    Ready,
    Empty,
}

impl Default for ContextReentrantTestStateContext {
    fn default() -> Self {
        ContextReentrantTestStateContext::Ready
    }
}

pub struct ContextReentrantTest {
    _state_stack: Vec<(String, ContextReentrantTestStateContext)>,
    __compartment: ContextReentrantTestCompartment,
    __next_compartment: Option<ContextReentrantTestCompartment>,
    _context_stack: Vec<ContextReentrantTestFrameContext>,
}

impl ContextReentrantTest {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            __compartment: ContextReentrantTestCompartment::new("Ready"),
            __next_compartment: None,
        };
let __frame_event = ContextReentrantTestFrameEvent::new("$>");
this.__kernel(__frame_event);
        this
    }

    fn __kernel(&mut self, __e: ContextReentrantTestFrameEvent) {
// Route event to current state
self.__router(&__e);
// Process any pending transition
while self.__next_compartment.is_some() {
    let next_compartment = self.__next_compartment.take().unwrap();
    // Exit current state
    let exit_event = ContextReentrantTestFrameEvent::new("<$");
    self.__router(&exit_event);
    // Switch to new compartment
    self.__compartment = next_compartment;
    // Enter new state (or forward event)
    if self.__compartment.forward_event.is_none() {
        let enter_event = ContextReentrantTestFrameEvent::new("$>");
        self.__router(&enter_event);
    } else {
        // Forward event to new state
        let forward_event = self.__compartment.forward_event.take().unwrap();
        if forward_event.message == "$>" {
            // Forwarding enter event - just send it
            self.__router(&forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            let enter_event = ContextReentrantTestFrameEvent::new("$>");
            self.__router(&enter_event);
            self.__router(&forward_event);
        }
    }
}
    }

    fn __router(&mut self, __e: &ContextReentrantTestFrameEvent) {
match self.__compartment.state.as_str() {
    "Ready" => self._state_Ready(__e),
    _ => {}
}
    }

    fn __transition(&mut self, next_compartment: ContextReentrantTestCompartment) {
self.__next_compartment = Some(next_compartment);
    }

    fn _state_stack_push(&mut self) {
let state_context = match self.__compartment.state.as_str() {
    "Ready" => ContextReentrantTestStateContext::Ready,
    _ => ContextReentrantTestStateContext::Empty,
};
self._state_stack.push((self.__compartment.state.clone(), state_context));
    }

    fn _state_stack_pop(&mut self) {
let (saved_state, state_context) = self._state_stack.pop().unwrap();
let exit_event = ContextReentrantTestFrameEvent::new("$<");
self.__router(&exit_event);
self.__compartment.state = saved_state;
match state_context {
    ContextReentrantTestStateContext::Ready => {}
    ContextReentrantTestStateContext::Empty => {}
}
    }

    pub fn outer(&mut self, x: i32) -> String {
let __e = ContextReentrantTestFrameEvent::new("outer");
match self.__compartment.state.as_str() {
            "Ready" => self._s_Ready_outer(&__e, x),
            _ => Default::default(),
        }
    }

    pub fn inner(&mut self, y: i32) -> String {
let __e = ContextReentrantTestFrameEvent::new("inner");
match self.__compartment.state.as_str() {
            "Ready" => self._s_Ready_inner(&__e, y),
            _ => Default::default(),
        }
    }

    pub fn get_both(&mut self, a: i32, b: i32) -> String {
let __e = ContextReentrantTestFrameEvent::new("get_both");
match self.__compartment.state.as_str() {
            "Ready" => self._s_Ready_get_both(&__e, a, b),
            _ => Default::default(),
        }
    }

    fn _state_Ready(&mut self, __e: &ContextReentrantTestFrameEvent) {
match __e.message.as_str() {
    _ => {}
}
    }

    fn _s_Ready_inner(&mut self, __e: &ContextReentrantTestFrameEvent, y: i32) -> String {
// Inner has its own context
// @@.y should be inner's param, not outer's
return format!("{}", /* @@.y */);
    }

    fn _s_Ready_outer(&mut self, __e: &ContextReentrantTestFrameEvent, x: i32) -> String {
// Set our return before calling inner
return "outer_initial".to_string();;

// Call inner - should NOT clobber our return
let inner_result = self.inner(/* @@.x - context params not implemented for Rust */ * 10);

// Our return should still be accessible
// Update it with combined result
return format!("outer:{},inner:{}", /* @@.x */, inner_result);
    }

    fn _s_Ready_get_both(&mut self, __e: &ContextReentrantTestFrameEvent, a: i32, b: i32) -> String {
// Test that we can access multiple params
let result_a = self.inner(/* @@.a - context params not implemented for Rust */);
let result_b = self.inner(/* @@.b - context params not implemented for Rust */);
// After both inner calls, @@.a and @@.b should still be our params
return format!("a={},b={},results={}+{}", /* @@.a */, /* @@.b */, result_a, result_b);
    }
}


fn main() {
    println!("=== Test 37: Context Reentrant ===");
    let mut s = ContextReentrantTest::new();

    // Test 1: Simple nesting - outer calls inner
    let result = s.outer(5);
    let expected = "outer:5,inner:50";
    assert_eq!(result, expected, "Expected '{}', got '{}'", expected, result);
    println!("1. outer(5) = '{}'", result);

    // Test 2: Inner alone
    let result = s.inner(42);
    assert_eq!(result, "42", "Expected '42', got '{}'", result);
    println!("2. inner(42) = '{}'", result);

    // Test 3: Multiple inner calls, params preserved
    let result = s.get_both(10, 20);
    let expected = "a=10,b=20,results=10+20";
    assert_eq!(result, expected, "Expected '{}', got '{}'", expected, result);
    println!("3. get_both(10, 20) = '{}'", result);

    println!("PASS: Context reentrant works correctly");
}
