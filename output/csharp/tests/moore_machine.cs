using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

// Moore Machine - output depends ONLY on state (output on entry)
// See: https://www.geeksforgeeks.org/mealy-and-moore-machines-in-toc/

class MooreMachineFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public MooreMachineFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public MooreMachineFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class MooreMachineFrameContext {
    public MooreMachineFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public MooreMachineFrameContext(MooreMachineFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class MooreMachineCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public MooreMachineFrameEvent forward_event;
    public MooreMachineCompartment parent_compartment;

    public MooreMachineCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public MooreMachineCompartment Copy() {
        MooreMachineCompartment c = new MooreMachineCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class MooreMachine {
    private List<MooreMachineCompartment> _state_stack;
    private MooreMachineCompartment __compartment;
    private MooreMachineCompartment __next_compartment;
    private List<MooreMachineFrameContext> _context_stack;
    public int current_output = 0;

    public MooreMachine() {
        _state_stack = new List<MooreMachineCompartment>();
        _context_stack = new List<MooreMachineFrameContext>();
        __compartment = new MooreMachineCompartment("Q0");
        __next_compartment = null;
        MooreMachineFrameEvent __frame_event = new MooreMachineFrameEvent("$>");
        MooreMachineFrameContext __ctx = new MooreMachineFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
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
                if (forward_event._message == "$>") {
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
        string state_name = __compartment.state;
        if (state_name == "Q0") {
            _state_Q0(__e);
        } else if (state_name == "Q1") {
            _state_Q1(__e);
        } else if (state_name == "Q2") {
            _state_Q2(__e);
        } else if (state_name == "Q3") {
            _state_Q3(__e);
        } else if (state_name == "Q4") {
            _state_Q4(__e);
        }
    }

    private void __transition(MooreMachineCompartment next) {
        __next_compartment = next;
    }

    public void i_0() {
        MooreMachineFrameEvent __e = new MooreMachineFrameEvent("i_0");
        MooreMachineFrameContext __ctx = new MooreMachineFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void i_1() {
        MooreMachineFrameEvent __e = new MooreMachineFrameEvent("i_1");
        MooreMachineFrameContext __ctx = new MooreMachineFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Q0(MooreMachineFrameEvent __e) {
        if (__e._message == "$>") {
            this.set_output(0);
        } else if (__e._message == "i_0") {
            { var __new_compartment = new MooreMachineCompartment("Q1");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "i_1") {
            { var __new_compartment = new MooreMachineCompartment("Q2");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Q1(MooreMachineFrameEvent __e) {
        if (__e._message == "$>") {
            this.set_output(0);
        } else if (__e._message == "i_0") {
            { var __new_compartment = new MooreMachineCompartment("Q1");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "i_1") {
            { var __new_compartment = new MooreMachineCompartment("Q3");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Q2(MooreMachineFrameEvent __e) {
        if (__e._message == "$>") {
            this.set_output(0);
        } else if (__e._message == "i_0") {
            { var __new_compartment = new MooreMachineCompartment("Q4");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "i_1") {
            { var __new_compartment = new MooreMachineCompartment("Q2");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Q3(MooreMachineFrameEvent __e) {
        if (__e._message == "$>") {
            this.set_output(1);
        } else if (__e._message == "i_0") {
            { var __new_compartment = new MooreMachineCompartment("Q4");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "i_1") {
            { var __new_compartment = new MooreMachineCompartment("Q2");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Q4(MooreMachineFrameEvent __e) {
        if (__e._message == "$>") {
            this.set_output(1);
        } else if (__e._message == "i_0") {
            { var __new_compartment = new MooreMachineCompartment("Q1");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "i_1") {
            { var __new_compartment = new MooreMachineCompartment("Q3");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
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

class Program {
    static void Main(string[] args) {
        Console.WriteLine("TAP version 14");
        Console.WriteLine("1..5");

        MooreMachine m = new MooreMachine();

        // Initial state Q0 has output 0
        if (m.get_output() == 0) {
            Console.WriteLine("ok 1 - moore initial state Q0 has output 0");
        } else {
            Console.WriteLine("not ok 1 - moore initial state Q0 has output 0 # got " + m.get_output());
        }

        // i_0: Q0 -> Q1 (output 0)
        m.i_0();
        if (m.get_output() == 0) {
            Console.WriteLine("ok 2 - moore Q1 has output 0");
        } else {
            Console.WriteLine("not ok 2 - moore Q1 has output 0 # got " + m.get_output());
        }

        // i_1: Q1 -> Q3 (output 1)
        m.i_1();
        if (m.get_output() == 1) {
            Console.WriteLine("ok 3 - moore Q3 has output 1");
        } else {
            Console.WriteLine("not ok 3 - moore Q3 has output 1 # got " + m.get_output());
        }

        // i_0: Q3 -> Q4 (output 1)
        m.i_0();
        if (m.get_output() == 1) {
            Console.WriteLine("ok 4 - moore Q4 has output 1");
        } else {
            Console.WriteLine("not ok 4 - moore Q4 has output 1 # got " + m.get_output());
        }

        // i_0: Q4 -> Q1 (output 0)
        m.i_0();
        if (m.get_output() == 0) {
            Console.WriteLine("ok 5 - moore Q1 has output 0 again");
        } else {
            Console.WriteLine("not ok 5 - moore Q1 has output 0 again # got " + m.get_output());
        }

        Console.WriteLine("# PASS - Moore machine outputs depend ONLY on state");
    }
}
