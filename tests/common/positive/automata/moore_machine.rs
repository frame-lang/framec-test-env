
// Moore Machine - output depends ONLY on state (output on entry)
// See: https://www.geeksforgeeks.org/mealy-and-moore-machines-in-toc/

#[allow(dead_code)]
struct MooreMachineFrameEvent {
    message: String,
    parameters: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl Clone for MooreMachineFrameEvent {
    fn clone(&self) -> Self {
        Self {
            message: self.message.clone(),
            parameters: std::collections::HashMap::new(),
        }
    }
}

impl MooreMachineFrameEvent {
    fn new(message: &str) -> Self {
        Self {
            message: message.to_string(),
            parameters: std::collections::HashMap::new(),
        }
    }
    fn new_with_params(message: &str, params: &std::collections::HashMap<String, String>) -> Self {
        Self {
            message: message.to_string(),
            parameters: params.iter().map(|(k, v)| (k.clone(), Box::new(v.clone()) as Box<dyn std::any::Any>)).collect(),
        }
    }
}

#[allow(dead_code)]
struct MooreMachineFrameContext {
    event: MooreMachineFrameEvent,
    _return: Option<Box<dyn std::any::Any>>,
    _data: std::collections::HashMap<String, Box<dyn std::any::Any>>,
}

impl MooreMachineFrameContext {
    fn new(event: MooreMachineFrameEvent, default_return: Option<Box<dyn std::any::Any>>) -> Self {
        Self {
            event,
            _return: default_return,
            _data: std::collections::HashMap::new(),
        }
    }
}

#[derive(Clone)]
enum MooreMachineStateContext {
    Q0,
    Q1,
    Q2,
    Q3,
    Q4,
    Empty,
}

impl Default for MooreMachineStateContext {
    fn default() -> Self {
        MooreMachineStateContext::Q0
    }
}

#[allow(dead_code)]
#[derive(Clone)]
struct MooreMachineCompartment {
    state: String,
    state_context: MooreMachineStateContext,
    enter_args: std::collections::HashMap<String, String>,
    exit_args: std::collections::HashMap<String, String>,
    forward_event: Option<MooreMachineFrameEvent>,
    parent_compartment: Option<Box<MooreMachineCompartment>>,
}

impl MooreMachineCompartment {
    fn new(state: &str) -> Self {
        let state_context = match state {
            "Q0" => MooreMachineStateContext::Q0,
            "Q1" => MooreMachineStateContext::Q1,
            "Q2" => MooreMachineStateContext::Q2,
            "Q3" => MooreMachineStateContext::Q3,
            "Q4" => MooreMachineStateContext::Q4,
            _ => MooreMachineStateContext::Empty,
        };
        Self {
            state: state.to_string(),
            state_context,
            enter_args: std::collections::HashMap::new(),
            exit_args: std::collections::HashMap::new(),
            forward_event: None,
            parent_compartment: None,
        }
    }
}

#[allow(dead_code)]
pub struct MooreMachine {
    _state_stack: Vec<MooreMachineCompartment>,
    __compartment: MooreMachineCompartment,
    __next_compartment: Option<MooreMachineCompartment>,
    _context_stack: Vec<MooreMachineFrameContext>,
    pub current_output: i32,
}

#[allow(non_snake_case)]
impl MooreMachine {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _context_stack: vec![],
            current_output: Default::default(),
            __compartment: MooreMachineCompartment::new("Q0"),
            __next_compartment: None,
        };
        let __frame_event = MooreMachineFrameEvent::new("$>");
        let __ctx = MooreMachineFrameContext::new(__frame_event, None);
        this._context_stack.push(__ctx);
        this.__kernel();
        this._context_stack.pop();
        this
    }

    fn __kernel(&mut self) {
        // Clone event from context stack (needed for borrow checker)
        let __e = self._context_stack.last().unwrap().event.clone();
        // Route event to current state
        self.__router(&__e);
        // Process any pending transition
        while self.__next_compartment.is_some() {
            let next_compartment = self.__next_compartment.take().unwrap();
            // Exit current state (with exit_args from current compartment)
            let exit_event = MooreMachineFrameEvent::new_with_params("<$", &self.__compartment.exit_args);
            self.__router(&exit_event);
            // Switch to new compartment
            self.__compartment = next_compartment;
            // Enter new state (or forward event)
            if self.__compartment.forward_event.is_none() {
                let enter_event = MooreMachineFrameEvent::new_with_params("$>", &self.__compartment.enter_args);
                self.__router(&enter_event);
            } else {
                // Forward event to new state
                let forward_event = self.__compartment.forward_event.take().unwrap();
                if forward_event.message == "$>" {
                    // Forwarding enter event - just send it
                    self.__router(&forward_event);
                } else {
                    // Forwarding other event - send $> first, then forward
                    let enter_event = MooreMachineFrameEvent::new_with_params("$>", &self.__compartment.enter_args);
                    self.__router(&enter_event);
                    self.__router(&forward_event);
                }
            }
        }
    }

    fn __router(&mut self, __e: &MooreMachineFrameEvent) {
        match self.__compartment.state.as_str() {
            "Q0" => self._state_Q0(__e),
            "Q1" => self._state_Q1(__e),
            "Q2" => self._state_Q2(__e),
            "Q3" => self._state_Q3(__e),
            "Q4" => self._state_Q4(__e),
            _ => {}
        }
    }

    fn __transition(&mut self, next_compartment: MooreMachineCompartment) {
        self.__next_compartment = Some(next_compartment);
    }

    fn __push_transition(&mut self, new_compartment: MooreMachineCompartment) {
        // Exit current state (old compartment still in place for routing)
        let exit_event = MooreMachineFrameEvent::new_with_params("<$", &self.__compartment.exit_args);
        self.__router(&exit_event);
        // Swap: old compartment moves to stack, new takes its place
        let old = std::mem::replace(&mut self.__compartment, new_compartment);
        self._state_stack.push(old);
        // Enter new state (or forward event) — matches kernel logic
        if self.__compartment.forward_event.is_none() {
            let enter_event = MooreMachineFrameEvent::new_with_params("$>", &self.__compartment.enter_args);
            self.__router(&enter_event);
        } else {
            let forward_event = self.__compartment.forward_event.take().unwrap();
            if forward_event.message == "$>" {
                self.__router(&forward_event);
            } else {
                let enter_event = MooreMachineFrameEvent::new_with_params("$>", &self.__compartment.enter_args);
                self.__router(&enter_event);
                self.__router(&forward_event);
            }
        }
    }

    pub fn i_0(&mut self) {
        let mut __e = MooreMachineFrameEvent::new("i_0");
        let mut __ctx = MooreMachineFrameContext::new(__e, None);
        self._context_stack.push(__ctx);
        self.__kernel();
        self._context_stack.pop();
    }

    pub fn i_1(&mut self) {
        let mut __e = MooreMachineFrameEvent::new("i_1");
        let mut __ctx = MooreMachineFrameContext::new(__e, None);
        self._context_stack.push(__ctx);
        self.__kernel();
        self._context_stack.pop();
    }

    fn _state_Q0(&mut self, __e: &MooreMachineFrameEvent) {
        match __e.message.as_str() {
            "$>" => { self._s_Q0_enter(__e); }
            "i_0" => { self._s_Q0_i_0(__e); }
            "i_1" => { self._s_Q0_i_1(__e); }
            _ => {}
        }
    }

    fn _state_Q1(&mut self, __e: &MooreMachineFrameEvent) {
        match __e.message.as_str() {
            "$>" => { self._s_Q1_enter(__e); }
            "i_0" => { self._s_Q1_i_0(__e); }
            "i_1" => { self._s_Q1_i_1(__e); }
            _ => {}
        }
    }

    fn _state_Q2(&mut self, __e: &MooreMachineFrameEvent) {
        match __e.message.as_str() {
            "$>" => { self._s_Q2_enter(__e); }
            "i_0" => { self._s_Q2_i_0(__e); }
            "i_1" => { self._s_Q2_i_1(__e); }
            _ => {}
        }
    }

    fn _state_Q3(&mut self, __e: &MooreMachineFrameEvent) {
        match __e.message.as_str() {
            "$>" => { self._s_Q3_enter(__e); }
            "i_0" => { self._s_Q3_i_0(__e); }
            "i_1" => { self._s_Q3_i_1(__e); }
            _ => {}
        }
    }

    fn _state_Q4(&mut self, __e: &MooreMachineFrameEvent) {
        match __e.message.as_str() {
            "$>" => { self._s_Q4_enter(__e); }
            "i_0" => { self._s_Q4_i_0(__e); }
            "i_1" => { self._s_Q4_i_1(__e); }
            _ => {}
        }
    }

    fn _s_Q0_enter(&mut self, __e: &MooreMachineFrameEvent) {
        self.set_output(0);
    }

    fn _s_Q0_i_1(&mut self, __e: &MooreMachineFrameEvent) {
        let mut __compartment = MooreMachineCompartment::new("Q2");
        __compartment.parent_compartment = Some(Box::new(self.__compartment.clone()));
        self.__transition(__compartment);
        return;
    }

    fn _s_Q0_i_0(&mut self, __e: &MooreMachineFrameEvent) {
        let mut __compartment = MooreMachineCompartment::new("Q1");
        __compartment.parent_compartment = Some(Box::new(self.__compartment.clone()));
        self.__transition(__compartment);
        return;
    }

    fn _s_Q1_i_1(&mut self, __e: &MooreMachineFrameEvent) {
        let mut __compartment = MooreMachineCompartment::new("Q3");
        __compartment.parent_compartment = Some(Box::new(self.__compartment.clone()));
        self.__transition(__compartment);
        return;
    }

    fn _s_Q1_enter(&mut self, __e: &MooreMachineFrameEvent) {
        self.set_output(0);
    }

    fn _s_Q1_i_0(&mut self, __e: &MooreMachineFrameEvent) {
        let mut __compartment = MooreMachineCompartment::new("Q1");
        __compartment.parent_compartment = Some(Box::new(self.__compartment.clone()));
        self.__transition(__compartment);
        return;
    }

    fn _s_Q2_i_0(&mut self, __e: &MooreMachineFrameEvent) {
        let mut __compartment = MooreMachineCompartment::new("Q4");
        __compartment.parent_compartment = Some(Box::new(self.__compartment.clone()));
        self.__transition(__compartment);
        return;
    }

    fn _s_Q2_i_1(&mut self, __e: &MooreMachineFrameEvent) {
        let mut __compartment = MooreMachineCompartment::new("Q2");
        __compartment.parent_compartment = Some(Box::new(self.__compartment.clone()));
        self.__transition(__compartment);
        return;
    }

    fn _s_Q2_enter(&mut self, __e: &MooreMachineFrameEvent) {
        self.set_output(0);
    }

    fn _s_Q3_enter(&mut self, __e: &MooreMachineFrameEvent) {
        self.set_output(1);
    }

    fn _s_Q3_i_1(&mut self, __e: &MooreMachineFrameEvent) {
        let mut __compartment = MooreMachineCompartment::new("Q2");
        __compartment.parent_compartment = Some(Box::new(self.__compartment.clone()));
        self.__transition(__compartment);
        return;
    }

    fn _s_Q3_i_0(&mut self, __e: &MooreMachineFrameEvent) {
        let mut __compartment = MooreMachineCompartment::new("Q4");
        __compartment.parent_compartment = Some(Box::new(self.__compartment.clone()));
        self.__transition(__compartment);
        return;
    }

    fn _s_Q4_enter(&mut self, __e: &MooreMachineFrameEvent) {
        self.set_output(1);
    }

    fn _s_Q4_i_1(&mut self, __e: &MooreMachineFrameEvent) {
        let mut __compartment = MooreMachineCompartment::new("Q3");
        __compartment.parent_compartment = Some(Box::new(self.__compartment.clone()));
        self.__transition(__compartment);
        return;
    }

    fn _s_Q4_i_0(&mut self, __e: &MooreMachineFrameEvent) {
        let mut __compartment = MooreMachineCompartment::new("Q1");
        __compartment.parent_compartment = Some(Box::new(self.__compartment.clone()));
        self.__transition(__compartment);
        return;
    }

    fn set_output(&mut self, value: i32) {
                    self.current_output = value;
    }

    pub fn get_output(&mut self) -> i32 {
                    return self.current_output;
    }
}

fn main() {
    println!("TAP version 14");
    println!("1..5");

    let mut m = MooreMachine::new();

    // Initial state Q0 has output 0
    if m.get_output() == 0 {
        println!("ok 1 - moore initial state Q0 has output 0");
    } else {
        println!("not ok 1 - moore initial state Q0 has output 0 # got {}", m.get_output());
    }

    // i_0: Q0 -> Q1 (output 0)
    m.i_0();
    if m.get_output() == 0 {
        println!("ok 2 - moore Q1 has output 0");
    } else {
        println!("not ok 2 - moore Q1 has output 0 # got {}", m.get_output());
    }

    // i_1: Q1 -> Q3 (output 1)
    m.i_1();
    if m.get_output() == 1 {
        println!("ok 3 - moore Q3 has output 1");
    } else {
        println!("not ok 3 - moore Q3 has output 1 # got {}", m.get_output());
    }

    // i_0: Q3 -> Q4 (output 1)
    m.i_0();
    if m.get_output() == 1 {
        println!("ok 4 - moore Q4 has output 1");
    } else {
        println!("not ok 4 - moore Q4 has output 1 # got {}", m.get_output());
    }

    // i_0: Q4 -> Q1 (output 0)
    m.i_0();
    if m.get_output() == 0 {
        println!("ok 5 - moore Q1 has output 0 again");
    } else {
        println!("not ok 5 - moore Q1 has output 0 again # got {}", m.get_output());
    }

    println!("# PASS - Moore machine outputs depend ONLY on state");
}

