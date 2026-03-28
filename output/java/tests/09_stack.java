import java.util.*;


import java.util.*;

class StackOpsFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    StackOpsFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    StackOpsFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class StackOpsFrameContext {
    StackOpsFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    StackOpsFrameContext(StackOpsFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class StackOpsCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    StackOpsFrameEvent forward_event;
    StackOpsCompartment parent_compartment;

    StackOpsCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    StackOpsCompartment copy() {
        StackOpsCompartment c = new StackOpsCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class StackOps {
    private ArrayList<StackOpsCompartment> _state_stack;
    private StackOpsCompartment __compartment;
    private StackOpsCompartment __next_compartment;
    private ArrayList<StackOpsFrameContext> _context_stack;

    public StackOps() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new StackOpsCompartment("Main");
        __next_compartment = null;
        StackOpsFrameEvent __frame_event = new StackOpsFrameEvent("$>");
        StackOpsFrameContext __ctx = new StackOpsFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(StackOpsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            StackOpsFrameEvent exit_event = new StackOpsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                StackOpsFrameEvent enter_event = new StackOpsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    StackOpsFrameEvent enter_event = new StackOpsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(StackOpsFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Main")) {
            _state_Main(__e);
        } else if (state_name.equals("Sub")) {
            _state_Sub(__e);
        }
    }

    private void __transition(StackOpsCompartment next) {
        __next_compartment = next;
    }

    public void push_and_go() {
        StackOpsFrameEvent __e = new StackOpsFrameEvent("push_and_go");
        StackOpsFrameContext __ctx = new StackOpsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void pop_back() {
        StackOpsFrameEvent __e = new StackOpsFrameEvent("pop_back");
        StackOpsFrameContext __ctx = new StackOpsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public String do_work() {
        StackOpsFrameEvent __e = new StackOpsFrameEvent("do_work");
        StackOpsFrameContext __ctx = new StackOpsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_state() {
        StackOpsFrameEvent __e = new StackOpsFrameEvent("get_state");
        StackOpsFrameContext __ctx = new StackOpsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Sub(StackOpsFrameEvent __e) {
        if (__e._message.equals("do_work")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Working in Sub";
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Sub";
            return;
        } else if (__e._message.equals("pop_back")) {
            System.out.println("Popping back to previous state");
            var __popped = _state_stack.remove(_state_stack.size() - 1);
            __transition(__popped);
            return;
        } else if (__e._message.equals("push_and_go")) {
            System.out.println("Already in Sub");
        }
    }

    private void _state_Main(StackOpsFrameEvent __e) {
        if (__e._message.equals("do_work")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Working in Main";
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Main";
            return;
        } else if (__e._message.equals("pop_back")) {
            System.out.println("Cannot pop - nothing on stack in Main");
        } else if (__e._message.equals("push_and_go")) {
            System.out.println("Pushing Main to stack, going to Sub");
            _state_stack.add(__compartment.copy());
            var __compartment = new StackOpsCompartment("Sub");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 09: Stack Push/Pop ===");
        var s = new StackOps();

        // Initial state should be Main
        String state = (String) s.get_state();
        if (!"Main".equals(state)) {
            throw new RuntimeException("Expected 'Main', got '" + state + "'");
        }
        System.out.println("Initial state: " + state);

        // Do work in Main
        String work = (String) s.do_work();
        if (!"Working in Main".equals(work)) {
            throw new RuntimeException("Expected 'Working in Main', got '" + work + "'");
        }
        System.out.println("do_work(): " + work);

        // Push and go to Sub
        s.push_and_go();
        state = (String) s.get_state();
        if (!"Sub".equals(state)) {
            throw new RuntimeException("Expected 'Sub', got '" + state + "'");
        }
        System.out.println("After push_and_go(): " + state);

        // Do work in Sub
        work = (String) s.do_work();
        if (!"Working in Sub".equals(work)) {
            throw new RuntimeException("Expected 'Working in Sub', got '" + work + "'");
        }
        System.out.println("do_work(): " + work);

        // Pop back to Main
        s.pop_back();
        state = (String) s.get_state();
        if (!"Main".equals(state)) {
            throw new RuntimeException("Expected 'Main' after pop, got '" + state + "'");
        }
        System.out.println("After pop_back(): " + state);

        System.out.println("PASS: Stack push/pop works correctly");
    }
}
