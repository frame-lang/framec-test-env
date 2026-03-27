import java.util.*;


import java.util.*;

class PersistStackFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    PersistStackFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    PersistStackFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class PersistStackFrameContext {
    PersistStackFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    PersistStackFrameContext(PersistStackFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class PersistStackCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    PersistStackFrameEvent forward_event;
    PersistStackCompartment parent_compartment;

    PersistStackCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    PersistStackCompartment copy() {
        PersistStackCompartment c = new PersistStackCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class PersistStack {
    private ArrayList<PersistStackCompartment> _state_stack;
    private PersistStackCompartment __compartment;
    private PersistStackCompartment __next_compartment;
    private ArrayList<PersistStackFrameContext> _context_stack;
    public int depth = 0;

    public PersistStack() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new PersistStackCompartment("Start");
        __next_compartment = null;
        PersistStackFrameEvent __frame_event = new PersistStackFrameEvent("$>");
        PersistStackFrameContext __ctx = new PersistStackFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
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
                if (forward_event._message.equals("$>")) {
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
        String state_name = __compartment.state;
        if (state_name.equals("Start")) {
            _state_Start(__e);
        } else if (state_name.equals("Middle")) {
            _state_Middle(__e);
        } else if (state_name.equals("End")) {
            _state_End(__e);
        }
    }

    private void __transition(PersistStackCompartment next) {
        __next_compartment = next;
    }

    public void push_and_go() {
        PersistStackFrameEvent __e = new PersistStackFrameEvent("push_and_go");
        PersistStackFrameContext __ctx = new PersistStackFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void pop_back() {
        PersistStackFrameEvent __e = new PersistStackFrameEvent("pop_back");
        PersistStackFrameContext __ctx = new PersistStackFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public String get_state() {
        PersistStackFrameEvent __e = new PersistStackFrameEvent("get_state");
        PersistStackFrameContext __ctx = new PersistStackFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_depth() {
        PersistStackFrameEvent __e = new PersistStackFrameEvent("get_depth");
        PersistStackFrameContext __ctx = new PersistStackFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Middle(PersistStackFrameEvent __e) {
        if (__e._message.equals("get_depth")) {
            _context_stack.get(_context_stack.size() - 1)._return = depth;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "middle";
            return;
        } else if (__e._message.equals("pop_back")) {
            depth = depth - 1;
            var __popped = _state_stack.remove(_state_stack.size() - 1);
            __transition(__popped);
            return;
        } else if (__e._message.equals("push_and_go")) {
            depth = depth + 1;
            _state_stack.add(__compartment.copy());
            var __compartment = new PersistStackCompartment("End");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Start(PersistStackFrameEvent __e) {
        if (__e._message.equals("get_depth")) {
            _context_stack.get(_context_stack.size() - 1)._return = depth;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "start";
            return;
        } else if (__e._message.equals("pop_back")) {
        } else if (__e._message.equals("push_and_go")) {
            depth = depth + 1;
            _state_stack.add(__compartment.copy());
            var __compartment = new PersistStackCompartment("Middle");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_End(PersistStackFrameEvent __e) {
        if (__e._message.equals("get_depth")) {
            _context_stack.get(_context_stack.size() - 1)._return = depth;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "end";
            return;
        } else if (__e._message.equals("pop_back")) {
            depth = depth - 1;
            var __popped = _state_stack.remove(_state_stack.size() - 1);
            __transition(__popped);
            return;
        } else if (__e._message.equals("push_and_go")) {
        }
    }

    private org.json.JSONObject __serComp(PersistStackCompartment comp) {
        if (comp == null) return null;
        var j = new org.json.JSONObject();
        j.put("state", comp.state);
        var sv = new org.json.JSONObject();
        for (var e : comp.state_vars.entrySet()) { sv.put(e.getKey(), e.getValue()); }
        j.put("state_vars", sv);
        j.put("parent", __serComp(comp.parent_compartment));
        return j;
    }

    private static PersistStackCompartment __deserComp(Object obj) {
        if (obj == null || obj.equals(org.json.JSONObject.NULL)) return null;
        var d = (org.json.JSONObject) obj;
        var c = new PersistStackCompartment(d.getString("state"));
        if (d.has("state_vars")) {
            var sv = d.getJSONObject("state_vars");
            for (var k : sv.keySet()) { c.state_vars.put(k, sv.get(k)); }
        }
        if (d.has("parent") && !d.isNull("parent")) {
            c.parent_compartment = __deserComp(d.get("parent"));
        }
        return c;
    }

    public String save_state() {
        var __j = new org.json.JSONObject();
        __j.put("_compartment", __serComp(__compartment));
        var __stack = new org.json.JSONArray();
        for (var c : _state_stack) { __stack.put(__serComp(c)); }
        __j.put("_state_stack", __stack);
        __j.put("depth", depth);
        return __j.toString();
    }

    public static PersistStack restore_state(String json) {
        var __j = new org.json.JSONObject(json);
        var __instance = new PersistStack();
        __instance.__compartment = __deserComp(__j.get("_compartment"));
        if (__j.has("_state_stack")) {
            var __stack = __j.getJSONArray("_state_stack");
            __instance._state_stack = new ArrayList<>();
            for (int i = 0; i < __stack.length(); i++) { __instance._state_stack.add(__deserComp(__stack.get(i))); }
        }
        if (__j.has("depth")) { __instance.depth = __j.getInt("depth"); }
        return __instance;
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 25: Persist Stack (Java) ===");

        var s1 = new PersistStack();
        s1.push_and_go();
        s1.push_and_go();
        if (!s1.get_state().equals("end") || s1.get_depth() != 2) {
            System.out.println("FAIL: build"); System.exit(1);
        }
        System.out.println("1. Built stack: " + s1.get_state() + ", depth=" + s1.get_depth());

        String json = s1.save_state();
        var data = new org.json.JSONObject(json);
        if (!data.getJSONObject("_compartment").getString("state").equals("End")) {
            System.out.println("FAIL: saved state"); System.exit(1);
        }
        if (data.getJSONArray("_state_stack").length() != 2) {
            System.out.println("FAIL: stack size"); System.exit(1);
        }
        System.out.println("2. Saved");

        var s2 = PersistStack.restore_state(json);
        if (!s2.get_state().equals("end") || s2.get_depth() != 2) {
            System.out.println("FAIL: restored"); System.exit(1);
        }
        System.out.println("3. Restored: " + s2.get_state() + ", depth=" + s2.get_depth());

        s2.pop_back();
        if (!s2.get_state().equals("middle") || s2.get_depth() != 1) {
            System.out.println("FAIL: pop1"); System.exit(1);
        }
        System.out.println("4. After pop: " + s2.get_state() + ", depth=" + s2.get_depth());

        s2.pop_back();
        if (!s2.get_state().equals("start") || s2.get_depth() != 0) {
            System.out.println("FAIL: pop2"); System.exit(1);
        }
        System.out.println("5. After 2nd pop: " + s2.get_state() + ", depth=" + s2.get_depth());

        System.out.println("PASS: Persist stack works correctly");
    }
}
