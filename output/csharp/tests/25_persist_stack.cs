using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;
using System.Text.Json;

class PersistStackFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public PersistStackFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public PersistStackFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class PersistStackFrameContext {
    public PersistStackFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public PersistStackFrameContext(PersistStackFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class PersistStackCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public PersistStackFrameEvent forward_event;
    public PersistStackCompartment parent_compartment;

    public PersistStackCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public PersistStackCompartment Copy() {
        PersistStackCompartment c = new PersistStackCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class PersistStack {
    private List<PersistStackCompartment> _state_stack;
    private PersistStackCompartment __compartment;
    private PersistStackCompartment __next_compartment;
    private List<PersistStackFrameContext> _context_stack;
    public int depth = 0;

    public PersistStack() {
        _state_stack = new List<PersistStackCompartment>();
        _context_stack = new List<PersistStackFrameContext>();
        __compartment = new PersistStackCompartment("Start");
        __next_compartment = null;
        PersistStackFrameEvent __frame_event = new PersistStackFrameEvent("$>");
        PersistStackFrameContext __ctx = new PersistStackFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(PersistStackFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            PersistStackFrameEvent exit_event = new PersistStackFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                PersistStackFrameEvent enter_event = new PersistStackFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    PersistStackFrameEvent enter_event = new PersistStackFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(PersistStackFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "Middle") {
            _state_Middle(__e);
        } else if (state_name == "End") {
            _state_End(__e);
        }
    }

    private void __transition(PersistStackCompartment next) {
        __next_compartment = next;
    }

    public void push_and_go() {
        PersistStackFrameEvent __e = new PersistStackFrameEvent("push_and_go");
        PersistStackFrameContext __ctx = new PersistStackFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public void pop_back() {
        PersistStackFrameEvent __e = new PersistStackFrameEvent("pop_back");
        PersistStackFrameContext __ctx = new PersistStackFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public string get_state() {
        PersistStackFrameEvent __e = new PersistStackFrameEvent("get_state");
        PersistStackFrameContext __ctx = new PersistStackFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int get_depth() {
        PersistStackFrameEvent __e = new PersistStackFrameEvent("get_depth");
        PersistStackFrameContext __ctx = new PersistStackFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Start(PersistStackFrameEvent __e) {
        if (__e._message == "get_depth") {
            _context_stack[_context_stack.Count - 1]._return = depth;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "start";
            return;
        } else if (__e._message == "pop_back") {
        } else if (__e._message == "push_and_go") {
            depth = depth + 1;
            _state_stack.Add(__compartment.Copy());
            { var __new_compartment = new PersistStackCompartment("Middle");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_End(PersistStackFrameEvent __e) {
        if (__e._message == "get_depth") {
            _context_stack[_context_stack.Count - 1]._return = depth;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "end";
            return;
        } else if (__e._message == "pop_back") {
            depth = depth - 1;
            var __popped = _state_stack[_state_stack.Count - 1]; _state_stack.RemoveAt(_state_stack.Count - 1);
            __transition(__popped);
            return;
        } else if (__e._message == "push_and_go") {
        }
    }

    private void _state_Middle(PersistStackFrameEvent __e) {
        if (__e._message == "get_depth") {
            _context_stack[_context_stack.Count - 1]._return = depth;
            return;
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "middle";
            return;
        } else if (__e._message == "pop_back") {
            depth = depth - 1;
            var __popped = _state_stack[_state_stack.Count - 1]; _state_stack.RemoveAt(_state_stack.Count - 1);
            __transition(__popped);
            return;
        } else if (__e._message == "push_and_go") {
            depth = depth + 1;
            _state_stack.Add(__compartment.Copy());
            { var __new_compartment = new PersistStackCompartment("End");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private object __SerComp(PersistStackCompartment comp) {
        if (comp == null) return null;
        var j = new Dictionary<string, object>();
        j["state"] = comp.state;
        var sv = new Dictionary<string, object>(comp.state_vars);
        j["state_vars"] = sv;
        j["parent"] = __SerComp(comp.parent_compartment);
        return j;
    }

    private static PersistStackCompartment __DeserComp(System.Text.Json.JsonElement el) {
        if (el.ValueKind == System.Text.Json.JsonValueKind.Null) return null;
        var c = new PersistStackCompartment(el.GetProperty("state").GetString());
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
        __j["depth"] = depth;
        var __opts = new System.Text.Json.JsonSerializerOptions { TypeInfoResolver = new System.Text.Json.Serialization.Metadata.DefaultJsonTypeInfoResolver() };
        return System.Text.Json.JsonSerializer.Serialize(__j, __opts);
    }

    public static PersistStack RestoreState(string json) {
        var __doc = System.Text.Json.JsonDocument.Parse(json);
        var __root = __doc.RootElement;
        var __instance = new PersistStack();
        __instance.__compartment = __DeserComp(__root.GetProperty("_compartment"));
        if (__root.TryGetProperty("_state_stack", out var __stack)) {
            __instance._state_stack = new List<PersistStackCompartment>();
            foreach (var item in __stack.EnumerateArray()) { __instance._state_stack.Add(__DeserComp(item)); }
        }
        if (__root.TryGetProperty("depth", out var __depth)) { __instance.depth = __depth.GetInt32(); }
        return __instance;
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 25: Persist Stack (C#) ===");

        var s1 = new PersistStack();
        s1.push_and_go();
        s1.push_and_go();
        if (s1.get_state() != "end" || s1.get_depth() != 2) {
            Console.WriteLine("FAIL: build"); Environment.Exit(1);
        }
        Console.WriteLine($"1. Built stack: {s1.get_state()}, depth={s1.get_depth()}");

        var json = s1.SaveState();
        var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;
        if (root.GetProperty("_compartment").GetProperty("state").GetString() != "End") {
            Console.WriteLine("FAIL: saved state"); Environment.Exit(1);
        }
        if (root.GetProperty("_state_stack").GetArrayLength() != 2) {
            Console.WriteLine("FAIL: stack size"); Environment.Exit(1);
        }
        Console.WriteLine("2. Saved");

        var s2 = PersistStack.RestoreState(json);
        if (s2.get_state() != "end" || s2.get_depth() != 2) {
            Console.WriteLine("FAIL: restored"); Environment.Exit(1);
        }
        Console.WriteLine($"3. Restored: {s2.get_state()}, depth={s2.get_depth()}");

        s2.pop_back();
        if (s2.get_state() != "middle" || s2.get_depth() != 1) {
            Console.WriteLine("FAIL: pop1"); Environment.Exit(1);
        }
        Console.WriteLine($"4. After pop: {s2.get_state()}, depth={s2.get_depth()}");

        s2.pop_back();
        if (s2.get_state() != "start" || s2.get_depth() != 0) {
            Console.WriteLine("FAIL: pop2"); Environment.Exit(1);
        }
        Console.WriteLine($"5. After 2nd pop: {s2.get_state()}, depth={s2.get_depth()}");

        Console.WriteLine("PASS: Persist stack works correctly");
    }
}
