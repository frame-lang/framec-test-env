import java.util.*;


import java.util.*;

// Moore Machine - output depends ONLY on state (output on entry)
// See: https://www.geeksforgeeks.org/mealy-and-moore-machines-in-toc/

class MooreMachineFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    MooreMachineFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    MooreMachineFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class MooreMachineFrameContext {
    MooreMachineFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    MooreMachineFrameContext(MooreMachineFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class MooreMachineCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    MooreMachineFrameEvent forward_event;
    MooreMachineCompartment parent_compartment;

    MooreMachineCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    MooreMachineCompartment copy() {
        MooreMachineCompartment c = new MooreMachineCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class MooreMachine {
    private ArrayList<MooreMachineCompartment> _state_stack;
    private MooreMachineCompartment __compartment;
    private MooreMachineCompartment __next_compartment;
    private ArrayList<MooreMachineFrameContext> _context_stack;
    public int current_output = 0;

    public MooreMachine() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new MooreMachineCompartment("Q0");
        __next_compartment = null;
        MooreMachineFrameEvent __frame_event = new MooreMachineFrameEvent("$>");
        MooreMachineFrameContext __ctx = new MooreMachineFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(MooreMachineFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            MooreMachineFrameEvent exit_event = new MooreMachineFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                MooreMachineFrameEvent enter_event = new MooreMachineFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    MooreMachineFrameEvent enter_event = new MooreMachineFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(MooreMachineFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Q0")) {
            _state_Q0(__e);
        } else if (state_name.equals("Q1")) {
            _state_Q1(__e);
        } else if (state_name.equals("Q2")) {
            _state_Q2(__e);
        } else if (state_name.equals("Q3")) {
            _state_Q3(__e);
        } else if (state_name.equals("Q4")) {
            _state_Q4(__e);
        }
    }

    private void __transition(MooreMachineCompartment next) {
        __next_compartment = next;
    }

    public void i_0() {
        MooreMachineFrameEvent __e = new MooreMachineFrameEvent("i_0");
        MooreMachineFrameContext __ctx = new MooreMachineFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void i_1() {
        MooreMachineFrameEvent __e = new MooreMachineFrameEvent("i_1");
        MooreMachineFrameContext __ctx = new MooreMachineFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Q0(MooreMachineFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.set_output(0);
        } else if (__e._message.equals("i_0")) {
            var __compartment = new MooreMachineCompartment("Q1");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("i_1")) {
            var __compartment = new MooreMachineCompartment("Q2");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Q2(MooreMachineFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.set_output(0);
        } else if (__e._message.equals("i_0")) {
            var __compartment = new MooreMachineCompartment("Q4");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("i_1")) {
            var __compartment = new MooreMachineCompartment("Q2");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Q3(MooreMachineFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.set_output(1);
        } else if (__e._message.equals("i_0")) {
            var __compartment = new MooreMachineCompartment("Q4");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("i_1")) {
            var __compartment = new MooreMachineCompartment("Q2");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Q4(MooreMachineFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.set_output(1);
        } else if (__e._message.equals("i_0")) {
            var __compartment = new MooreMachineCompartment("Q1");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("i_1")) {
            var __compartment = new MooreMachineCompartment("Q3");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Q1(MooreMachineFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.set_output(0);
        } else if (__e._message.equals("i_0")) {
            var __compartment = new MooreMachineCompartment("Q1");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("i_1")) {
            var __compartment = new MooreMachineCompartment("Q3");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void set_output(int value) {
                    this.current_output = value;
    }

    public int get_output() {
                    return this.current_output;
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("TAP version 14");
        System.out.println("1..5");

        MooreMachine m = new MooreMachine();

        // Initial state Q0 has output 0
        if (m.get_output() == 0) {
            System.out.println("ok 1 - moore initial state Q0 has output 0");
        } else {
            System.out.println("not ok 1 - moore initial state Q0 has output 0 # got " + m.get_output());
        }

        // i_0: Q0 -> Q1 (output 0)
        m.i_0();
        if (m.get_output() == 0) {
            System.out.println("ok 2 - moore Q1 has output 0");
        } else {
            System.out.println("not ok 2 - moore Q1 has output 0 # got " + m.get_output());
        }

        // i_1: Q1 -> Q3 (output 1)
        m.i_1();
        if (m.get_output() == 1) {
            System.out.println("ok 3 - moore Q3 has output 1");
        } else {
            System.out.println("not ok 3 - moore Q3 has output 1 # got " + m.get_output());
        }

        // i_0: Q3 -> Q4 (output 1)
        m.i_0();
        if (m.get_output() == 1) {
            System.out.println("ok 4 - moore Q4 has output 1");
        } else {
            System.out.println("not ok 4 - moore Q4 has output 1 # got " + m.get_output());
        }

        // i_0: Q4 -> Q1 (output 0)
        m.i_0();
        if (m.get_output() == 0) {
            System.out.println("ok 5 - moore Q1 has output 0 again");
        } else {
            System.out.println("not ok 5 - moore Q1 has output 0 again # got " + m.get_output());
        }

        System.out.println("# PASS - Moore machine outputs depend ONLY on state");
    }
}
