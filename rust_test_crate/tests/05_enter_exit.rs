use std::collections::HashMap;

pub struct EnterExit {
    _state: String,
    _state_stack: Vec<Box<dyn std::any::Any>>,
    _state_context: HashMap<String, Box<dyn std::any::Any>>,
    log: Vec<String>,
}

impl EnterExit {
    pub fn new() -> Self {
        let mut this = Self {
            _state_stack: vec![],
            _state_context: HashMap::from([]),
            log: Vec::new(),
            _state: String::from("Off"),
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
    "Off" => {
        self._s_Off_enter();
    }
    "On" => {
        self._s_On_enter();
    }
    _ => {}
}
    }

    fn _exit(&mut self) {
match self._state.as_str() {
            "Off" => { self._s_Off_exit(); }
            "On" => { self._s_On_exit(); }
            _ => {}
        }
    }

    pub fn toggle(&mut self) {
match self._state.as_str() {
            "Off" => { self._s_Off_toggle(); }
            "On" => { self._s_On_toggle(); }
            _ => {}
        }
    }

    pub fn get_log(&mut self) -> Vec<String> {
match self._state.as_str() {
            "Off" => self._s_Off_get_log(),
            "On" => self._s_On_get_log(),
            _ => Default::default(),
        }
    }

    fn _s_On_get_log(&mut self) -> Vec<String> {
self.log.clone()
    }

    fn _s_On_enter(&mut self) {
self.log.push("enter:On".to_string());
println!("Entered On state");
    }

    fn _s_On_toggle(&mut self) {
self._transition("Off");
    }

    fn _s_On_exit(&mut self) {
self.log.push("exit:On".to_string());
println!("Exiting On state");
    }

    fn _s_Off_toggle(&mut self) {
self._transition("On");
    }

    fn _s_Off_get_log(&mut self) -> Vec<String> {
self.log.clone()
    }

    fn _s_Off_enter(&mut self) {
self.log.push("enter:Off".to_string());
println!("Entered Off state");
    }

    fn _s_Off_exit(&mut self) {
self.log.push("exit:Off".to_string());
println!("Exiting Off state");
    }
}


fn main() {
    println!("=== Test 05: Enter/Exit Handlers ===");
    let mut s = EnterExit::new();

    // Initial enter should have been called
    let log = s.get_log();
    assert!(log.contains(&"enter:Off".to_string()), "Expected 'enter:Off' in log, got {:?}", log);
    println!("After construction: {:?}", log);

    // Toggle to On - should exit Off, enter On
    s.toggle();
    let log = s.get_log();
    assert!(log.contains(&"exit:Off".to_string()), "Expected 'exit:Off' in log, got {:?}", log);
    assert!(log.contains(&"enter:On".to_string()), "Expected 'enter:On' in log, got {:?}", log);
    println!("After toggle to On: {:?}", log);

    // Toggle back to Off - should exit On, enter Off
    s.toggle();
    let log = s.get_log();
    let enter_off_count = log.iter().filter(|s| *s == "enter:Off").count();
    assert_eq!(enter_off_count, 2, "Expected 2 'enter:Off' entries, got {:?}", log);
    assert!(log.contains(&"exit:On".to_string()), "Expected 'exit:On' in log, got {:?}", log);
    println!("After toggle to Off: {:?}", log);

    println!("PASS: Enter/Exit handlers work correctly");
}
