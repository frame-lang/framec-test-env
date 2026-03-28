using System;
using System.Collections.Generic;

// @@skip
// Persist tests need System.Text.Json pipeline support for C#

using System;
using System.Collections.Generic;

class PersistTestFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public PersistTestFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public PersistTestFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class PersistTestFrameContext {
    public PersistTestFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public PersistTestFrameContext(PersistTestFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class PersistTestCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public PersistTestFrameEvent forward_event;
    public PersistTestCompartment parent_compartment;

    public PersistTestCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public PersistTestCompartment Copy() {
        PersistTestCompartment c = new PersistTestCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class PersistTest {
    private List<PersistTestCompartment> _state_stack;
    private PersistTestCompartment __compartment;
    private PersistTestCompartment __next_compartment;
    private List<PersistTestFrameContext> _context_stack;
    public int value = 0;
    public string name = "default";

    public PersistTest() {
        _state_stack = new List<PersistTestCompartment>();
        _context_stack = new List<PersistTestFrameContext>();
        __compartment = new PersistTestCompartment("Idle");
        __next_compartment = null;
        PersistTestFrameEvent __frame_event = new PersistTestFrameEvent("$>");
        PersistTestFrameContext __ctx = new PersistTestFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(PersistTestFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            PersistTestFrameEvent exit_event = new PersistTestFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                PersistTestFrameEvent enter_event = new PersistTestFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    PersistTestFrameEvent enter_event = new PersistTestFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(PersistTestFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    private void __transition(PersistTestCompartment next) {
        __next_compartment = next;
    }

    public void set_value(int v) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["v"] = v;
        PersistTestFrameEvent __e = new PersistTestFrameEvent("set_value", __params);
        PersistTestFrameContext __ctx = new PersistTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public int get_value() {
        PersistTestFrameEvent __e = new PersistTestFrameEvent("get_value");
        PersistTestFrameContext __ctx = new PersistTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public void go_active() {
        PersistTestFrameEvent __e = new PersistTestFrameEvent("go_active");
        PersistTestFrameContext __ctx = new PersistTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void go_idle() {
        PersistTestFrameEvent __e = new PersistTestFrameEvent("go_idle");
        PersistTestFrameContext __ctx = new PersistTestFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Active(PersistTestFrameEvent __e) {
        if (__e._message == "get_value") {
            _context_stack[_context_stack.Count - 1]._return = value;
            return;
        } else if (__e._message == "go_active") {
        } else if (__e._message == "go_idle") {
            { var __new_compartment = new PersistTestCompartment("Idle");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "set_value") {
            var v = (int) __e._parameters["v"];
            value = v * 2;
        }
    }

    private void _state_Idle(PersistTestFrameEvent __e) {
        if (__e._message == "get_value") {
            _context_stack[_context_stack.Count - 1]._return = value;
            return;
        } else if (__e._message == "go_active") {
            { var __new_compartment = new PersistTestCompartment("Active");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "go_idle") {
        } else if (__e._message == "set_value") {
            var v = (int) __e._parameters["v"];
            value = v;
        }
    }

    private object __SerComp(PersistTestCompartment comp) {
        if (comp == null) return null;
        var j = new Dictionary<string, object>();
        j["state"] = comp.state;
        var sv = new Dictionary<string, object>(comp.state_vars);
        j["state_vars"] = sv;
        j["parent"] = __SerComp(comp.parent_compartment);
        return j;
    }

    private static PersistTestCompartment __DeserComp(object obj) {
        if (obj == null) return null;
        var d = (Dictionary<string, object>) obj;
        var c = new PersistTestCompartment((string)d["state"]);
        if (d.ContainsKey("state_vars")) {
            var sv = (Dictionary<string, object>)d["state_vars"];
            foreach (var kv in sv) { c.state_vars[kv.Key] = kv.Value; }
        }
        if (d.ContainsKey("parent") && d["parent"] != null) {
            c.parent_compartment = __DeserComp(d["parent"]);
        }
        return c;
    }

    public string SaveState() {
        var __j = new Dictionary<string, object>();
        __j["_compartment"] = __SerComp(__compartment);
        var __stack = new List<object>();
        foreach (var c in _state_stack) { __stack.Add(__SerComp(c)); }
        __j["_state_stack"] = __stack;
        __j["value"] = value;
        __j["name"] = name;
        return System.Text.Json.JsonSerializer.Serialize(__j);
    }

    public static PersistTest RestoreState(string json) {
        var __j = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, object>>(json);
        var __instance = new PersistTest();
        __instance.__compartment = __DeserComp(__j["_compartment"]);
        if (__j.ContainsKey("_state_stack")) {
            var __stack = (List<object>)__j["_state_stack"];
            __instance._state_stack = new List<PersistTestCompartment>();
            foreach (var item in __stack) { __instance._state_stack.Add(__DeserComp(item)); }
        }
        if (__j.ContainsKey("value")) { __instance.value = __j["value"]; }
        if (__j.ContainsKey("name")) { __instance.name = __j["name"]; }
        return __instance;
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 23: Persist Basic (C#) ===");
        Console.WriteLine("SKIP: Persist tests need System.Text.Json pipeline support");
    }
}
