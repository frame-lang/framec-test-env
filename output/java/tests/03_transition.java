import java.util.*;


import java.util.*;

class WithTransitionFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    WithTransitionFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    WithTransitionFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class WithTransitionFrameContext {
    WithTransitionFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    WithTransitionFrameContext(WithTransitionFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class WithTransitionCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    WithTransitionFrameEvent forward_event;
    WithTransitionCompartment parent_compartment;

    WithTransitionCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    WithTransitionCompartment copy() {
        WithTransitionCompartment c = new WithTransitionCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class WithTransition {
    private ArrayList<WithTransitionCompartment> _state_stack;
    private WithTransitionCompartment __compartment;
    private WithTransitionCompartment __next_compartment;
    private ArrayList<WithTransitionFrameContext> _context_stack;

    public WithTransition() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new WithTransitionCompartment("First");
        __next_compartment = null;
        WithTransitionFrameEvent __frame_event = new WithTransitionFrameEvent("$>");
        WithTransitionFrameContext __ctx = new WithTransitionFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(WithTransitionFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            WithTransitionFrameEvent exit_event = new WithTransitionFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                WithTransitionFrameEvent enter_event = new WithTransitionFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    WithTransitionFrameEvent enter_event = new WithTransitionFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(WithTransitionFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("First")) {
            _state_First(__e);
        } else if (state_name.equals("Second")) {
            _state_Second(__e);
        }
    }

    private void __transition(WithTransitionCompartment next) {
        __next_compartment = next;
    }

    public void next() {
        WithTransitionFrameEvent __e = new WithTransitionFrameEvent("next");
        WithTransitionFrameContext __ctx = new WithTransitionFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public String get_state() {
        WithTransitionFrameEvent __e = new WithTransitionFrameEvent("get_state");
        WithTransitionFrameContext __ctx = new WithTransitionFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_First(WithTransitionFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "First";
            return;
        } else if (__e._message.equals("next")) {
            var __compartment = new WithTransitionCompartment("Second");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Second(WithTransitionFrameEvent __e) {
        if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Second";
            return;
        } else if (__e._message.equals("next")) {
            var __compartment = new WithTransitionCompartment("First");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 03: State Transitions ===");
        var s = new WithTransition();

        String state = s.get_state();
        if (!state.equals("First")) {
            System.out.println("FAIL: Expected 'First', got '" + state + "'");
            System.exit(1);
        }
        System.out.println("Initial state: " + state);

        s.next();
        state = s.get_state();
        if (!state.equals("Second")) {
            System.out.println("FAIL: Expected 'Second', got '" + state + "'");
            System.exit(1);
        }
        System.out.println("After first next(): " + state);

        s.next();
        state = s.get_state();
        if (!state.equals("First")) {
            System.out.println("FAIL: Expected 'First', got '" + state + "'");
            System.exit(1);
        }
        System.out.println("After second next(): " + state);

        System.out.println("PASS: State transitions work correctly");
    }
}
