import java.util.*;


import java.util.*;

class PersistRoundtripFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    PersistRoundtripFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    PersistRoundtripFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class PersistRoundtripFrameContext {
    PersistRoundtripFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    PersistRoundtripFrameContext(PersistRoundtripFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class PersistRoundtripCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    PersistRoundtripFrameEvent forward_event;
    PersistRoundtripCompartment parent_compartment;

    PersistRoundtripCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    PersistRoundtripCompartment copy() {
        PersistRoundtripCompartment c = new PersistRoundtripCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class PersistRoundtrip {
    private ArrayList<PersistRoundtripCompartment> _state_stack;
    private PersistRoundtripCompartment __compartment;
    private PersistRoundtripCompartment __next_compartment;
    private ArrayList<PersistRoundtripFrameContext> _context_stack;
    public int counter = 0;
    public String history = "";
    public String mode = "normal";

    public PersistRoundtrip() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new PersistRoundtripCompartment("Idle");
        __next_compartment = null;
        PersistRoundtripFrameEvent __frame_event = new PersistRoundtripFrameEvent("$>");
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
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
                if (forward_event._message.equals("$>")) {
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
        String state_name = __compartment.state;
        if (state_name.equals("Idle")) {
            _state_Idle(__e);
        } else if (state_name.equals("Active")) {
            _state_Active(__e);
        }
    }

    private void __transition(PersistRoundtripCompartment next) {
        __next_compartment = next;
    }

    public void set_counter(int v) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("v", v);
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("set_counter", __params);
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public int get_counter() {
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("get_counter");
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public void go_active() {
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("go_active");
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void go_idle() {
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("go_idle");
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public String get_state() {
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("get_state");
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public void add_history(String entry) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("entry", entry);
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("add_history", __params);
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public String get_history() {
        PersistRoundtripFrameEvent __e = new PersistRoundtripFrameEvent("get_history");
        PersistRoundtripFrameContext __ctx = new PersistRoundtripFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Idle(PersistRoundtripFrameEvent __e) {
        if (__e._message.equals("add_history")) {
            var entry = (String) __e._parameters.get("entry");
            history = history + entry + ",";
        } else if (__e._message.equals("get_counter")) {
            _context_stack.get(_context_stack.size() - 1)._return = counter;
            return;
        } else if (__e._message.equals("get_history")) {
            _context_stack.get(_context_stack.size() - 1)._return = history;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "idle";
            return;
        } else if (__e._message.equals("go_active")) {
            this.add_history("idle->active");
            var __compartment = new PersistRoundtripCompartment("Active");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("go_idle")) {
        } else if (__e._message.equals("set_counter")) {
            var v = (int) __e._parameters.get("v");
            counter = v;
        }
    }

    private void _state_Active(PersistRoundtripFrameEvent __e) {
        if (__e._message.equals("add_history")) {
            var entry = (String) __e._parameters.get("entry");
            history = history + entry + ",";
        } else if (__e._message.equals("get_counter")) {
            _context_stack.get(_context_stack.size() - 1)._return = counter;
            return;
        } else if (__e._message.equals("get_history")) {
            _context_stack.get(_context_stack.size() - 1)._return = history;
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "active";
            return;
        } else if (__e._message.equals("go_active")) {
        } else if (__e._message.equals("go_idle")) {
            this.add_history("active->idle");
            var __compartment = new PersistRoundtripCompartment("Idle");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("set_counter")) {
            var v = (int) __e._parameters.get("v");
            counter = v * 2;
        }
    }

    private org.json.JSONObject __serComp(PersistRoundtripCompartment comp) {
        if (comp == null) return null;
        var j = new org.json.JSONObject();
        j.put("state", comp.state);
        var sv = new org.json.JSONObject();
        for (var e : comp.state_vars.entrySet()) { sv.put(e.getKey(), e.getValue()); }
        j.put("state_vars", sv);
        j.put("parent", __serComp(comp.parent_compartment));
        return j;
    }

    private static PersistRoundtripCompartment __deserComp(Object obj) {
        if (obj == null || obj.equals(org.json.JSONObject.NULL)) return null;
        var d = (org.json.JSONObject) obj;
        var c = new PersistRoundtripCompartment(d.getString("state"));
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
        __j.put("counter", counter);
        __j.put("history", history);
        __j.put("mode", mode);
        return __j.toString();
    }

    public static PersistRoundtrip restore_state(String json) {
        var __j = new org.json.JSONObject(json);
        var __instance = new PersistRoundtrip();
        __instance.__compartment = __deserComp(__j.get("_compartment"));
        if (__j.has("_state_stack")) {
            var __stack = __j.getJSONArray("_state_stack");
            __instance._state_stack = new ArrayList<>();
            for (int i = 0; i < __stack.length(); i++) { __instance._state_stack.add(__deserComp(__stack.get(i))); }
        }
        if (__j.has("counter")) { __instance.counter = __j.getInt("counter"); }
        if (__j.has("history")) { __instance.history = __j.getString("history"); }
        if (__j.has("mode")) { __instance.mode = __j.getString("mode"); }
        return __instance;
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 24: Persist Roundtrip (Java) ===");

        var s1 = new PersistRoundtrip();
        s1.add_history("idle:start");
        s1.go_active();
        s1.set_counter(3);
        s1.add_history("active:work");

        if (!s1.get_state().equals("active")) { System.out.println("FAIL: state"); System.exit(1); }
        if (s1.get_counter() != 6) { System.out.println("FAIL: counter " + s1.get_counter()); System.exit(1); }
        System.out.println("1. State: " + s1.get_state() + ", counter: " + s1.get_counter());
        System.out.println("   History: " + s1.get_history());

        String json = s1.save_state();
        System.out.println("2. Saved");

        var s2 = PersistRoundtrip.restore_state(json);
        if (!s2.get_state().equals("active")) { System.out.println("FAIL: restored state"); System.exit(1); }
        if (s2.get_counter() != 6) { System.out.println("FAIL: restored counter"); System.exit(1); }
        System.out.println("3. Restored: " + s2.get_state() + ", counter: " + s2.get_counter());

        s2.set_counter(2);
        if (s2.get_counter() != 4) { System.out.println("FAIL: post-restore counter"); System.exit(1); }
        System.out.println("4. Counter after set_counter(2): " + s2.get_counter());

        if (!s2.get_history().contains("idle:start")) { System.out.println("FAIL: history"); System.exit(1); }
        System.out.println("5. History preserved: " + s2.get_history());

        s2.go_idle();
        s2.set_counter(10);
        if (s2.get_counter() != 10) { System.out.println("FAIL: idle counter"); System.exit(1); }
        System.out.println("6. After go_idle: " + s2.get_state() + ", counter: " + s2.get_counter());

        System.out.println("PASS: Persist roundtrip works correctly");
    }
}
