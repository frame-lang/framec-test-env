using System;
using System.Collections.Generic;

// @@skip â HSM persist restore reinitializes state vars via constructor $> event

using System;
using System.Collections.Generic;
using System.Text.Json;

class HSMPersistFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public HSMPersistFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public HSMPersistFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMPersistFrameContext {
    public HSMPersistFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public HSMPersistFrameContext(HSMPersistFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class HSMPersistCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public HSMPersistFrameEvent forward_event;
    public HSMPersistCompartment parent_compartment;

    public HSMPersistCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public HSMPersistCompartment Copy() {
        HSMPersistCompartment c = new HSMPersistCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMPersist {
    private List<HSMPersistCompartment> _state_stack;
    private HSMPersistCompartment __compartment;
    private HSMPersistCompartment __next_compartment;
    private List<HSMPersistFrameContext> _context_stack;
    public int parent_count_init = 100;

    public HSMPersist() {
        _state_stack = new List<HSMPersistCompartment>();
        _context_stack = new List<HSMPersistFrameContext>();
        __compartment = new HSMPersistCompartment("Parent");
        __next_compartment = null;
        HSMPersistFrameEvent __frame_event = new HSMPersistFrameEvent("$>");
        HSMPersistFrameContext __ctx = new HSMPersistFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(HSMPersistFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            HSMPersistFrameEvent exit_event = new HSMPersistFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                HSMPersistFrameEvent enter_event = new HSMPersistFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    HSMPersistFrameEvent enter_event = new HSMPersistFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(HSMPersistFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Parent") {
            _state_Parent(__e);
        } else if (state_name == "Child") {
            _state_Child(__e);
        }
    }

    private void __transition(HSMPersistCompartment next) {
        __next_compartment = next;
    }

    public void increment_child() {
        HSMPersistFrameEvent __e = new HSMPersistFrameEvent("increment_child");
        HSMPersistFrameContext __ctx = new HSMPersistFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void increment_parent() {
        HSMPersistFrameEvent __e = new HSMPersistFrameEvent("increment_parent");
        HSMPersistFrameContext __ctx = new HSMPersistFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public int get_child_count() {
        HSMPersistFrameEvent __e = new HSMPersistFrameEvent("get_child_count");
        HSMPersistFrameContext __ctx = new HSMPersistFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int get_parent_count() {
        HSMPersistFrameEvent __e = new HSMPersistFrameEvent("get_parent_count");
        HSMPersistFrameContext __ctx = new HSMPersistFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_state() {
        HSMPersistFrameEvent __e = new HSMPersistFrameEvent("get_state");
        HSMPersistFrameContext __ctx = new HSMPersistFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Child(HSMPersistFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && __sv_comp.state != "Child") { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message == "$>") {
            if (!__sv_comp.state_vars.ContainsKey("child_count")) {
                __sv_comp.state_vars["child_count"] = 0;
            }
        } else if (__e._message == "get_child_count") {
            _context_stack[_context_stack.Count - 1]._return = (int) __sv_comp.state_vars["child_count"];
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Child";
            return;
        } else if (__e._message == "increment_child") {
            __sv_comp.state_vars["child_count"] = (int) __sv_comp.state_vars["child_count"] + 1;
        }
    }

    private void _state_Parent(HSMPersistFrameEvent __e) {
        if (__e._message == "get_child_count") {
            _context_stack[_context_stack.Count - 1]._return = -1;
            return;
        } else if (__e._message == "get_parent_count") {
            _context_stack[_context_stack.Count - 1]._return = (int) __compartment.state_vars["parent_count"];
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Parent";
            return;
        } else if (__e._message == "increment_child") {
        } else if (__e._message == "increment_parent") {
            __compartment.state_vars["parent_count"] = (int) __compartment.state_vars["parent_count"] + 1;
        }
    }

    private object __SerComp(HSMPersistCompartment comp) {
        if (comp == null) return null;
        var j = new Dictionary<string, object>();
        j["state"] = comp.state;
        var sv = new Dictionary<string, object>(comp.state_vars);
        j["state_vars"] = sv;
        j["parent"] = __SerComp(comp.parent_compartment);
        return j;
    }

    private static HSMPersistCompartment __DeserComp(System.Text.Json.JsonElement el) {
        if (el.ValueKind == System.Text.Json.JsonValueKind.Null) return null;
        var c = new HSMPersistCompartment(el.GetProperty("state").GetString());
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
        __j["parent_count_init"] = parent_count_init;
        var __opts = new System.Text.Json.JsonSerializerOptions { TypeInfoResolver = new System.Text.Json.Serialization.Metadata.DefaultJsonTypeInfoResolver() };
        return System.Text.Json.JsonSerializer.Serialize(__j, __opts);
    }

    public static HSMPersist RestoreState(string json) {
        var __doc = System.Text.Json.JsonDocument.Parse(json);
        var __root = __doc.RootElement;
        var __instance = new HSMPersist();
        __instance.__compartment = __DeserComp(__root.GetProperty("_compartment"));
        if (__root.TryGetProperty("_state_stack", out var __stack)) {
            __instance._state_stack = new List<HSMPersistCompartment>();
            foreach (var item in __stack.EnumerateArray()) { __instance._state_stack.Add(__DeserComp(item)); }
        }
        if (__root.TryGetProperty("parent_count_init", out var __parent_count_init)) { __instance.parent_count_init = __parent_count_init.GetInt32(); }
        return __instance;
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 51: HSM Persistence (C#) ===");

        var s1 = new HSMPersist();
        s1.increment_child();
        s1.increment_child();
        s1.increment_child();

        if (s1.get_child_count() != 3) {
            Console.WriteLine($"FAIL: child_count {s1.get_child_count()}"); Environment.Exit(1);
        }
        Console.WriteLine($"1. child_count: {s1.get_child_count()}");

        var json = s1.SaveState();
        Console.WriteLine($"2. Saved: {json.Length} chars");

        var s2 = HSMPersist.RestoreState(json);
        if (s2.get_state() != "Child") {
            Console.WriteLine($"FAIL: state {s2.get_state()}"); Environment.Exit(1);
        }
        Console.WriteLine($"3. Restored state: {s2.get_state()}");

        if (s2.get_child_count() != 3) {
            Console.WriteLine($"FAIL: restored child_count {s2.get_child_count()}"); Environment.Exit(1);
        }
        Console.WriteLine($"4. child_count preserved: {s2.get_child_count()}");

        s2.increment_child();
        if (s2.get_child_count() != 4) {
            Console.WriteLine($"FAIL: post-restore {s2.get_child_count()}"); Environment.Exit(1);
        }
        Console.WriteLine($"5. After increment: {s2.get_child_count()}");

        Console.WriteLine("PASS: HSM persistence works correctly");
    }
}
