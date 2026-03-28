using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;
using System.Text.Json;

class PersistRoundtripFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public PersistRoundtripFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public PersistRoundtripFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class PersistRoundtripFrameContext {
    public PersistRoundtripFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public PersistRoundtripFrameContext(PersistRoundtripFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class PersistRoundtripCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public PersistRoundtripFrameEvent forward_event;
    public PersistRoundtripCompartment parent_compartment;

    public PersistRoundtripCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public PersistRoundtripCompartment Copy() {
        PersistRoundtripCompartment c = new PersistRoundtripCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class PersistRoundtrip {
    private List<PersistRoundtripCompartment> _state_stack;
    private PersistRoundtripCompartment __compartment;
    private PersistRoundtripCompartment __next_compartment;
    private List<PersistRoundtripFrameContext> _context_stack;
    public int counter = 0;
    public string history = "";
    public string mode = "normal";

    public PersistRoundtrip() {
        _state_stack = new List<PersistRoundtripCompartment>();
        _context_stack = new List<PersistRoundtripFrameContext>();
        __compartment = new PersistRoundtripCompartment("Idle");
        __next_compartment = null;
        PersistRoundtripFrameEvent __frame_event = new PersistRoundtripFrameEvent("$>");
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(PersistRoundtripFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            PersistRoundtripFrameEvent exit_event = new PersistRoundtripFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                PersistRoundtripFrameEvent enter_event = new PersistRoundtripFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    PersistRoundtripFrameEvent enter_event = new PersistRoundtripFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(PersistRoundtripFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    private void __transition(PersistRoundtripCompartment next) {
        __next_compartment = next;
    }

    public void set_counter(int v) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["v"] = v;
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("set_counter", __params);
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public int get_counter() {
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("get_counter");
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public void go_active() {
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("go_active");
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void go_idle() {
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("go_idle");
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public string get_state() {
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("get_state");
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public void add_history(string entry) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["entry"] = entry;
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("add_history", __params);
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public string get_history() {
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("get_history");
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Active(PersistRoundtripFrameEvent __e) {
        if (__e._message == "add_history") {
            var entry = (string) __e._parameters["entry"];
            history = history + entry + ",";
        } else if (__e._message == "get_counter") {
            _context_stack[_context_stack.Count - 1]._return = counter;
            return;
        } else if (__e._message == "get_history") {
            _context_stack[_context_stack.Count - 1]._return = history;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "active";
            return;
        } else if (__e._message == "go_active") {
        } else if (__e._message == "go_idle") {
            this.add_history("active->idle");
            { var __new_compartment = new PersistRoundtripCompartment("Idle");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "set_counter") {
            var v = (int) __e._parameters["v"];
            counter = v * 2;
        }
    }

    private void _state_Idle(PersistRoundtripFrameEvent __e) {
        if (__e._message == "add_history") {
            var entry = (string) __e._parameters["entry"];
            history = history + entry + ",";
        } else if (__e._message == "get_counter") {
            _context_stack[_context_stack.Count - 1]._return = counter;
            return;
        } else if (__e._message == "get_history") {
            _context_stack[_context_stack.Count - 1]._return = history;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "idle";
            return;
        } else if (__e._message == "go_active") {
            this.add_history("idle->active");
            { var __new_compartment = new PersistRoundtripCompartment("Active");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        } else if (__e._message == "go_idle") {
        } else if (__e._message == "set_counter") {
            var v = (int) __e._parameters["v"];
            counter = v;
        }
    }

    private object __SerComp(PersistRoundtripCompartment comp) {
        if (comp == null) return null;
        var j = new Dictionary<string, object>();
        j["state"] = comp.state;
        var sv = new Dictionary<string, object>(comp.state_vars);
        j["state_vars"] = sv;
        j["parent"] = __SerComp(comp.parent_compartment);
        return j;
    }

    private static PersistRoundtripCompartment __DeserComp(System.Text.Json.JsonElement el) {
        if (el.ValueKind == System.Text.Json.JsonValueKind.Null) return null;
        var c = new PersistRoundtripCompartment(el.GetProperty("state").GetString());
        if (el.TryGetProperty("state_vars", out var sv) && sv.ValueKind == System.Text.Json.JsonValueKind.Object) {
            foreach (var kv in sv.EnumerateObject()) {
                if (kv.Value.ValueKind == System.Text.Json.JsonValueKind.Number) c.state_vars[kv.Name] = kv.Value.GetInt32();
                else if (kv.Value.ValueKind == System.Text.Json.JsonValueKind.String) c.state_vars[kv.Name] = kv.Value.GetString();
                else c.state_vars[kv.Name] = kv.Value.ToString();
            }
        }
        if (el.TryGetProperty("parent", out var p) && p.ValueKind != System.Text.Json.JsonValueKind.Null) {
            c.parent_compartment = __DeserComp(p);
        }
        return c;
    }

    public string SaveState() {
        var __j = new Dictionary<string, object>();
        __j["_compartment"] = __SerComp(__compartment);
        var __stack = new List<object>();
        foreach (var c in _state_stack) { __stack.Add(__SerComp(c)); }
        __j["_state_stack"] = __stack;
        __j["counter"] = counter;
        __j["history"] = history;
        __j["mode"] = mode;
        var __opts = new System.Text.Json.JsonSerializerOptions { TypeInfoResolver = new System.Text.Json.Serialization.Metadata.DefaultJsonTypeInfoResolver() };
        return System.Text.Json.JsonSerializer.Serialize(__j, __opts);
    }

    public static PersistRoundtrip RestoreState(string json) {
        var __doc = System.Text.Json.JsonDocument.Parse(json);
        var __root = __doc.RootElement;
        var __instance = new PersistRoundtrip();
        __instance.__compartment = __DeserComp(__root.GetProperty("_compartment"));
        if (__root.TryGetProperty("_state_stack", out var __stack)) {
            __instance._state_stack = new List<PersistRoundtripCompartment>();
            foreach (var item in __stack.EnumerateArray()) { __instance._state_stack.Add(__DeserComp(item)); }
        }
        if (__root.TryGetProperty("counter", out var __counter)) { __instance.counter = __counter.GetInt32(); }
        if (__root.TryGetProperty("history", out var __history)) { __instance.history = __history.GetString(); }
        if (__root.TryGetProperty("mode", out var __mode)) { __instance.mode = __mode.GetString(); }
        return __instance;
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 24: Persist Roundtrip (C#) ===");

        var s1 = new PersistRoundtrip();
        s1.add_history("idle:start");
        s1.go_active();
        s1.set_counter(3);
        s1.add_history("active:work");

        if (s1.get_state() != "active") { Console.WriteLine("FAIL: state"); Environment.Exit(1); }
        if (s1.get_counter() != 6) { Console.WriteLine($"FAIL: counter {s1.get_counter()}"); Environment.Exit(1); }
        Console.WriteLine($"1. State: {s1.get_state()}, counter: {s1.get_counter()}");
        Console.WriteLine($"   History: {s1.get_history()}");

        var json = s1.SaveState();
        Console.WriteLine("2. Saved");

        var s2 = PersistRoundtrip.RestoreState(json);
        if (s2.get_state() != "active") { Console.WriteLine("FAIL: restored state"); Environment.Exit(1); }
        if (s2.get_counter() != 6) { Console.WriteLine("FAIL: restored counter"); Environment.Exit(1); }
        Console.WriteLine($"3. Restored: {s2.get_state()}, counter: {s2.get_counter()}");

        s2.set_counter(2);
        if (s2.get_counter() != 4) { Console.WriteLine("FAIL: post-restore counter"); Environment.Exit(1); }
        Console.WriteLine($"4. Counter after set_counter(2): {s2.get_counter()}");

        if (!s2.get_history().Contains("idle:start")) { Console.WriteLine("FAIL: history"); Environment.Exit(1); }
        Console.WriteLine($"5. History preserved: {s2.get_history()}");

        s2.go_idle();
        s2.set_counter(10);
        if (s2.get_counter() != 10) { Console.WriteLine("FAIL: idle counter"); Environment.Exit(1); }
        Console.WriteLine($"6. After go_idle: {s2.get_state()}, counter: {s2.get_counter()}");

        Console.WriteLine("PASS: Persist roundtrip works correctly");
    }
}
