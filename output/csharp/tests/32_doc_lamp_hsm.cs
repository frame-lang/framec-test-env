using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class LampHSMFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public LampHSMFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public LampHSMFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class LampHSMFrameContext {
    public LampHSMFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public LampHSMFrameContext(LampHSMFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class LampHSMCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public LampHSMFrameEvent forward_event;
    public LampHSMCompartment parent_compartment;

    public LampHSMCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public LampHSMCompartment Copy() {
        LampHSMCompartment c = new LampHSMCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class LampHSM {
    private List<LampHSMCompartment> _state_stack;
    private LampHSMCompartment __compartment;
    private LampHSMCompartment __next_compartment;
    private List<LampHSMFrameContext> _context_stack;
    public string color = "white";
    public bool lamp_on = false;

    public LampHSM() {
        _state_stack = new List<LampHSMCompartment>();
        _context_stack = new List<LampHSMFrameContext>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new LampHSMCompartment("ColorBehavior");
        this.__compartment = new LampHSMCompartment("Off");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        LampHSMFrameEvent __frame_event = new LampHSMFrameEvent("$>");
        LampHSMFrameContext __ctx = new LampHSMFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(LampHSMFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            LampHSMFrameEvent exit_event = new LampHSMFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                LampHSMFrameEvent enter_event = new LampHSMFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    LampHSMFrameEvent enter_event = new LampHSMFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(LampHSMFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Off") {
            _state_Off(__e);
        } else if (state_name == "On") {
            _state_On(__e);
        } else if (state_name == "ColorBehavior") {
            _state_ColorBehavior(__e);
        }
    }

    private void __transition(LampHSMCompartment next) {
        __next_compartment = next;
    }

    public void turnOn() {
        LampHSMFrameEvent __e = new LampHSMFrameEvent("turnOn");
        LampHSMFrameContext __ctx = new LampHSMFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void turnOff() {
        LampHSMFrameEvent __e = new LampHSMFrameEvent("turnOff");
        LampHSMFrameContext __ctx = new LampHSMFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public string getColor() {
        LampHSMFrameEvent __e = new LampHSMFrameEvent("getColor");
        LampHSMFrameContext __ctx = new LampHSMFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public void setColor(string color) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["color"] = color;
        LampHSMFrameEvent __e = new LampHSMFrameEvent("setColor", __params);
        LampHSMFrameContext __ctx = new LampHSMFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public bool isLampOn() {
        LampHSMFrameEvent __e = new LampHSMFrameEvent("isLampOn");
        LampHSMFrameContext __ctx = new LampHSMFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (bool) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_On(LampHSMFrameEvent __e) {
        if (__e._message == "<$") {
            this.turnOffLamp();
        } else if (__e._message == "$>") {
            this.turnOnLamp();
        } else if (__e._message == "isLampOn") {
            _context_stack[_context_stack.Count - 1]._return = this.lamp_on;
            return;
        } else if (__e._message == "turnOff") {
            { var __new_compartment = new LampHSMCompartment("Off");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else {
            _state_ColorBehavior(__e);
        }
    }

    private void _state_Off(LampHSMFrameEvent __e) {
        if (__e._message == "isLampOn") {
            _context_stack[_context_stack.Count - 1]._return = this.lamp_on;
            return;
        } else if (__e._message == "turnOn") {
            { var __new_compartment = new LampHSMCompartment("On");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else {
            _state_ColorBehavior(__e);
        }
    }

    private void _state_ColorBehavior(LampHSMFrameEvent __e) {
        if (__e._message == "getColor") {
            _context_stack[_context_stack.Count - 1]._return = this.color;
            return;
        } else if (__e._message == "setColor") {
            var color = (string) __e._parameters["color"];
            this.color = color;
        }
    }

    private void turnOnLamp() {
                    this.lamp_on = true;
    }

    private void turnOffLamp() {
                    this.lamp_on = false;
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 32: Doc Lamp HSM ===");
        var lamp = new LampHSM();

        // Color behavior available in both states
        if ((string)lamp.getColor() != "white") {
            Console.WriteLine("FAIL: Expected 'white', got '" + lamp.getColor() + "'");
            Environment.Exit(1);
        }
        lamp.setColor("red");
        if ((string)lamp.getColor() != "red") {
            Console.WriteLine("FAIL: Expected 'red', got '" + lamp.getColor() + "'");
            Environment.Exit(1);
        }

        // Turn on
        lamp.turnOn();
        if ((bool)lamp.isLampOn() != true) {
            Console.WriteLine("FAIL: Lamp should be on");
            Environment.Exit(1);
        }

        // Color still works when on
        lamp.setColor("green");
        if ((string)lamp.getColor() != "green") {
            Console.WriteLine("FAIL: Expected 'green', got '" + lamp.getColor() + "'");
            Environment.Exit(1);
        }

        // Turn off
        lamp.turnOff();
        if ((bool)lamp.isLampOn() != false) {
            Console.WriteLine("FAIL: Lamp should be off");
            Environment.Exit(1);
        }

        // Color still works when off
        if ((string)lamp.getColor() != "green") {
            Console.WriteLine("FAIL: Expected 'green', got '" + lamp.getColor() + "'");
            Environment.Exit(1);
        }

        Console.WriteLine("PASS: HSM lamp works correctly");
    }
}
