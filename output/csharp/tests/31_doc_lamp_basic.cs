using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class LampFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public LampFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public LampFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class LampFrameContext {
    public LampFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public LampFrameContext(LampFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class LampCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public LampFrameEvent forward_event;
    public LampCompartment parent_compartment;

    public LampCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public LampCompartment Copy() {
        LampCompartment c = new LampCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class Lamp {
    private List<LampCompartment> _state_stack;
    private LampCompartment __compartment;
    private LampCompartment __next_compartment;
    private List<LampFrameContext> _context_stack;
    public string color = "white";
    public bool switch_closed = false;

    public Lamp() {
        _state_stack = new List<LampCompartment>();
        _context_stack = new List<LampFrameContext>();
        __compartment = new LampCompartment("Off");
        __next_compartment = null;
        LampFrameEvent __frame_event = new LampFrameEvent("$>");
        LampFrameContext __ctx = new LampFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(LampFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            LampFrameEvent exit_event = new LampFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                LampFrameEvent enter_event = new LampFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    LampFrameEvent enter_event = new LampFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(LampFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Off") {
            _state_Off(__e);
        } else if (state_name == "On") {
            _state_On(__e);
        }
    }

    private void __transition(LampCompartment next) {
        __next_compartment = next;
    }

    public void turnOn() {
        LampFrameEvent __e = new LampFrameEvent("turnOn");
        LampFrameContext __ctx = new LampFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void turnOff() {
        LampFrameEvent __e = new LampFrameEvent("turnOff");
        LampFrameContext __ctx = new LampFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public string getColor() {
        LampFrameEvent __e = new LampFrameEvent("getColor");
        LampFrameContext __ctx = new LampFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public void setColor(string color) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["color"] = color;
        LampFrameEvent __e = new LampFrameEvent("setColor", __params);
        LampFrameContext __ctx = new LampFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public bool isSwitchClosed() {
        LampFrameEvent __e = new LampFrameEvent("isSwitchClosed");
        LampFrameContext __ctx = new LampFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Off(LampFrameEvent __e) {
        if (__e._message == "getColor") {
            _context_stack[_context_stack.Count - 1]._return = this.color;
            return;
        } else if (__e._message == "isSwitchClosed") {
            _context_stack[_context_stack.Count - 1]._return = this.switch_closed;
            return;
        } else if (__e._message == "setColor") {
            var color = (string) __e._parameters["color"];
            this.color = color;
        } else if (__e._message == "turnOn") {
            { var __new_compartment = new LampCompartment("On");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_On(LampFrameEvent __e) {
        if (__e._message == "<$") {
            this.openSwitch();
        } else if (__e._message == "$>") {
            this.closeSwitch();
        } else if (__e._message == "getColor") {
            _context_stack[_context_stack.Count - 1]._return = this.color;
            return;
        } else if (__e._message == "isSwitchClosed") {
            _context_stack[_context_stack.Count - 1]._return = this.switch_closed;
            return;
        } else if (__e._message == "setColor") {
            var color = (string) __e._parameters["color"];
            this.color = color;
        } else if (__e._message == "turnOff") {
            { var __new_compartment = new LampCompartment("Off");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void closeSwitch() {
                    this.switch_closed = true;
    }

    private void openSwitch() {
                    this.switch_closed = false;
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 31: Doc Lamp Basic ===");
        var lamp = new Lamp();

        // Initially off
        if ((bool)lamp.isSwitchClosed() != false) {
            Console.WriteLine("FAIL: Switch should be open initially");
            Environment.Exit(1);
        }

        // Turn on - should close switch
        lamp.turnOn();
        if ((bool)lamp.isSwitchClosed() != true) {
            Console.WriteLine("FAIL: Switch should be closed after turnOn");
            Environment.Exit(1);
        }

        // Check color
        if ((string)lamp.getColor() != "white") {
            Console.WriteLine("FAIL: Expected 'white', got '" + lamp.getColor() + "'");
            Environment.Exit(1);
        }

        // Set color
        lamp.setColor("blue");
        if ((string)lamp.getColor() != "blue") {
            Console.WriteLine("FAIL: Expected 'blue', got '" + lamp.getColor() + "'");
            Environment.Exit(1);
        }

        // Turn off - should open switch
        lamp.turnOff();
        if ((bool)lamp.isSwitchClosed() != false) {
            Console.WriteLine("FAIL: Switch should be open after turnOff");
            Environment.Exit(1);
        }

        Console.WriteLine("PASS: Basic lamp works correctly");
    }
}
