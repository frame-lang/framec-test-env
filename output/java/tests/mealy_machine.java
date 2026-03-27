import java.util.*;


import java.util.*;

// Mealy Machine - output depends on state AND input (output on transitions)
// See: https://www.geeksforgeeks.org/mealy-and-moore-machines-in-toc/

class MealyMachineFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    MealyMachineFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    MealyMachineFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class MealyMachineFrameContext {
    MealyMachineFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    MealyMachineFrameContext(MealyMachineFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class MealyMachineCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    MealyMachineFrameEvent forward_event;
    MealyMachineCompartment parent_compartment;

    MealyMachineCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    MealyMachineCompartment copy() {
        MealyMachineCompartment c = new MealyMachineCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class MealyMachine {
    private ArrayList<MealyMachineCompartment> _state_stack;
    private MealyMachineCompartment __compartment;
    private MealyMachineCompartment __next_compartment;
    private ArrayList<MealyMachineFrameContext> _context_stack;
    public int last_output = -1;

    public MealyMachine() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new MealyMachineCompartment("Q0");
        __next_compartment = null;
        MealyMachineFrameEvent __frame_event = new MealyMachineFrameEvent("$>");
        MealyMachineFrameContext __ctx = new MealyMachineFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(MealyMachineFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            MealyMachineFrameEvent exit_event = new MealyMachineFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                MealyMachineFrameEvent enter_event = new MealyMachineFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    MealyMachineFrameEvent enter_event = new MealyMachineFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(MealyMachineFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Q0")) {
            _state_Q0(__e);
        } else if (state_name.equals("Q1")) {
            _state_Q1(__e);
        } else if (state_name.equals("Q2")) {
            _state_Q2(__e);
        }
    }

    private void __transition(MealyMachineCompartment next) {
        __next_compartment = next;
    }

    public void i_0() {
        MealyMachineFrameEvent __e = new MealyMachineFrameEvent("i_0");
        MealyMachineFrameContext __ctx = new MealyMachineFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void i_1() {
        MealyMachineFrameEvent __e = new MealyMachineFrameEvent("i_1");
        MealyMachineFrameContext __ctx = new MealyMachineFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Q2(MealyMachineFrameEvent __e) {
        if (__e._message.equals("i_0")) {
            this.emit_output(1);
            var __compartment = new MealyMachineCompartment("Q1");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("i_1")) {
            this.emit_output(0);
            var __compartment = new MealyMachineCompartment("Q2");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Q0(MealyMachineFrameEvent __e) {
        if (__e._message.equals("i_0")) {
            this.emit_output(0);
            var __compartment = new MealyMachineCompartment("Q1");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("i_1")) {
            this.emit_output(0);
            var __compartment = new MealyMachineCompartment("Q2");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Q1(MealyMachineFrameEvent __e) {
        if (__e._message.equals("i_0")) {
            this.emit_output(0);
            var __compartment = new MealyMachineCompartment("Q1");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("i_1")) {
            this.emit_output(1);
            var __compartment = new MealyMachineCompartment("Q2");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void emit_output(int value) {
                    this.last_output = value;
    }

    public int get_last_output() {
                    return this.last_output;
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("TAP version 14");
        System.out.println("1..4");

        MealyMachine m = new MealyMachine();

        m.i_0();  // Q0 -> Q1, output 0
        if (m.get_last_output() == 0) {
            System.out.println("ok 1 - mealy i_0 from Q0 outputs 0");
        } else {
            System.out.println("not ok 1 - mealy i_0 from Q0 outputs 0 # got " + m.get_last_output());
        }

        m.i_0();  // Q1 -> Q1, output 0
        if (m.get_last_output() == 0) {
            System.out.println("ok 2 - mealy i_0 from Q1 outputs 0");
        } else {
            System.out.println("not ok 2 - mealy i_0 from Q1 outputs 0 # got " + m.get_last_output());
        }

        m.i_1();  // Q1 -> Q2, output 1
        if (m.get_last_output() == 1) {
            System.out.println("ok 3 - mealy i_1 from Q1 outputs 1");
        } else {
            System.out.println("not ok 3 - mealy i_1 from Q1 outputs 1 # got " + m.get_last_output());
        }

        m.i_0();  // Q2 -> Q1, output 1
        if (m.get_last_output() == 1) {
            System.out.println("ok 4 - mealy i_0 from Q2 outputs 1");
        } else {
            System.out.println("not ok 4 - mealy i_0 from Q2 outputs 1 # got " + m.get_last_output());
        }

        System.out.println("# PASS - Mealy machine outputs depend on state AND input");
    }
}
