using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

// Mealy Machine - output depends on state AND input (output on transitions)
// See: https://www.geeksforgeeks.org/mealy-and-moore-machines-in-toc/

class MealyMachineFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public MealyMachineFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public MealyMachineFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class MealyMachineFrameContext {
    public MealyMachineFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public MealyMachineFrameContext(MealyMachineFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class MealyMachineCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public MealyMachineFrameEvent forward_event;
    public MealyMachineCompartment parent_compartment;

    public MealyMachineCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public MealyMachineCompartment Copy() {
        MealyMachineCompartment c = new MealyMachineCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class MealyMachine {
    private List<MealyMachineCompartment> _state_stack;
    private MealyMachineCompartment __compartment;
    private MealyMachineCompartment __next_compartment;
    private List<MealyMachineFrameContext> _context_stack;
    public int last_output = -1;

    public MealyMachine() {
        _state_stack = new List<MealyMachineCompartment>();
        _context_stack = new List<MealyMachineFrameContext>();
        __compartment = new MealyMachineCompartment("Q0");
        __next_compartment = null;
        MealyMachineFrameEvent __frame_event = new MealyMachineFrameEvent("$>");
        MealyMachineFrameContext __ctx = new MealyMachineFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
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
                if (forward_event._message == "$>") {
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
        string state_name = __compartment.state;
        if (state_name == "Q0") {
            _state_Q0(__e);
        } else if (state_name == "Q1") {
            _state_Q1(__e);
        } else if (state_name == "Q2") {
            _state_Q2(__e);
        }
    }

    private void __transition(MealyMachineCompartment next) {
        __next_compartment = next;
    }

    public void i_0() {
        MealyMachineFrameEvent __e = new MealyMachineFrameEvent("i_0");
        MealyMachineFrameContext __ctx = new MealyMachineFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void i_1() {
        MealyMachineFrameEvent __e = new MealyMachineFrameEvent("i_1");
        MealyMachineFrameContext __ctx = new MealyMachineFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Q0(MealyMachineFrameEvent __e) {
        if (__e._message == "i_0") {
            this.emit_output(0);
            { var __new_compartment = new MealyMachineCompartment("Q1");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "i_1") {
            this.emit_output(0);
            { var __new_compartment = new MealyMachineCompartment("Q2");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Q2(MealyMachineFrameEvent __e) {
        if (__e._message == "i_0") {
            this.emit_output(1);
            { var __new_compartment = new MealyMachineCompartment("Q1");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "i_1") {
            this.emit_output(0);
            { var __new_compartment = new MealyMachineCompartment("Q2");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Q1(MealyMachineFrameEvent __e) {
        if (__e._message == "i_0") {
            this.emit_output(0);
            { var __new_compartment = new MealyMachineCompartment("Q1");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "i_1") {
            this.emit_output(1);
            { var __new_compartment = new MealyMachineCompartment("Q2");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
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

class Program {
    static void Main(string[] args) {
        Console.WriteLine("TAP version 14");
        Console.WriteLine("1..4");

        MealyMachine m = new MealyMachine();

        m.i_0();  // Q0 -> Q1, output 0
        if (m.get_last_output() == 0) {
            Console.WriteLine("ok 1 - mealy i_0 from Q0 outputs 0");
        } else {
            Console.WriteLine("not ok 1 - mealy i_0 from Q0 outputs 0 # got " + m.get_last_output());
        }

        m.i_0();  // Q1 -> Q1, output 0
        if (m.get_last_output() == 0) {
            Console.WriteLine("ok 2 - mealy i_0 from Q1 outputs 0");
        } else {
            Console.WriteLine("not ok 2 - mealy i_0 from Q1 outputs 0 # got " + m.get_last_output());
        }

        m.i_1();  // Q1 -> Q2, output 1
        if (m.get_last_output() == 1) {
            Console.WriteLine("ok 3 - mealy i_1 from Q1 outputs 1");
        } else {
            Console.WriteLine("not ok 3 - mealy i_1 from Q1 outputs 1 # got " + m.get_last_output());
        }

        m.i_0();  // Q2 -> Q1, output 1
        if (m.get_last_output() == 1) {
            Console.WriteLine("ok 4 - mealy i_0 from Q2 outputs 1");
        } else {
            Console.WriteLine("not ok 4 - mealy i_0 from Q2 outputs 1 # got " + m.get_last_output());
        }

        Console.WriteLine("# PASS - Mealy machine outputs depend on state AND input");
    }
}
