import java.util.*;


import java.util.*;

class PersistTestFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    PersistTestFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    PersistTestFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class PersistTestFrameContext {
    PersistTestFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    PersistTestFrameContext(PersistTestFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class PersistTestCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    PersistTestFrameEvent forward_event;
    PersistTestCompartment parent_compartment;

    PersistTestCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    PersistTestCompartment copy() {
        PersistTestCompartment c = new PersistTestCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class PersistTest {
    private ArrayList<PersistTestCompartment> _state_stack;
    private PersistTestCompartment __compartment;
    private PersistTestCompartment __next_compartment;
    private ArrayList<PersistTestFrameContext> _context_stack;
    public int value = 0;
    public String name = "default";

    public PersistTest() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new PersistTestCompartment("Idle");
        __next_compartment = null;
        PersistTestFrameEvent __frame_event = new PersistTestFrameEvent("$>");
        PersistTestFrameContext __ctx = new PersistTestFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
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
                if (forward_event._message.equals("$>")) {
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
        String state_name = __compartment.state;
        if (state_name.equals("Idle")) {
            _state_Idle(__e);
        } else if (state_name.equals("Active")) {
            _state_Active(__e);
        }
    }

    private void __transition(PersistTestCompartment next) {
        __next_compartment = next;
    }

    public void set_value(int v) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("v", v);
        PersistTestFrameEvent __e = new PersistTestFrameEvent("set_value", __params);
        PersistTestFrameContext __ctx = new PersistTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public int get_value() {
        PersistTestFrameEvent __e = new PersistTestFrameEvent("get_value");
        PersistTestFrameContext __ctx = new PersistTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public void go_active() {
        PersistTestFrameEvent __e = new PersistTestFrameEvent("go_active");
        PersistTestFrameContext __ctx = new PersistTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void go_idle() {
        PersistTestFrameEvent __e = new PersistTestFrameEvent("go_idle");
        PersistTestFrameContext __ctx = new PersistTestFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Active(PersistTestFrameEvent __e) {
        if (__e._message.equals("get_value")) {
            _context_stack.get(_context_stack.size() - 1)._return = value;
            return;
        } else if (__e._message.equals("go_active")) {
        } else if (__e._message.equals("go_idle")) {
            var __compartment = new PersistTestCompartment("Idle");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("set_value")) {
            var v = (int) __e._parameters.get("v");
            value = v * 2;
        }
    }

    private void _state_Idle(PersistTestFrameEvent __e) {
        if (__e._message.equals("get_value")) {
            _context_stack.get(_context_stack.size() - 1)._return = value;
            return;
        } else if (__e._message.equals("go_active")) {
            var __compartment = new PersistTestCompartment("Active");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else if (__e._message.equals("go_idle")) {
        } else if (__e._message.equals("set_value")) {
            var v = (int) __e._parameters.get("v");
            value = v;
        }
    }

    private org.json.JSONObject __serComp(PersistTestCompartment comp) {
        if (comp == null) return null;
        var j = new org.json.JSONObject();
        j.put("state", comp.state);
        var sv = new org.json.JSONObject();
        for (var e : comp.state_vars.entrySet()) { sv.put(e.getKey(), e.getValue()); }
        j.put("state_vars", sv);
        j.put("parent", __serComp(comp.parent_compartment));
        return j;
    }

    private static PersistTestCompartment __deserComp(Object obj) {
        if (obj == null || obj.equals(org.json.JSONObject.NULL)) return null;
        var d = (org.json.JSONObject) obj;
        var c = new PersistTestCompartment(d.getString("state"));
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
        __j.put("value", value);
        __j.put("name", name);
        return __j.toString();
    }

    public static PersistTest restore_state(String json) {
        var __j = new org.json.JSONObject(json);
        var __instance = new PersistTest();
        __instance.__compartment = __deserComp(__j.get("_compartment"));
        if (__j.has("_state_stack")) {
            var __stack = __j.getJSONArray("_state_stack");
            __instance._state_stack = new ArrayList<>();
            for (int i = 0; i < __stack.length(); i++) { __instance._state_stack.add(__deserComp(__stack.get(i))); }
        }
        if (__j.has("value")) { __instance.value = __j.getInt("value"); }
        if (__j.has("name")) { __instance.name = __j.getString("name"); }
        return __instance;
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 23: Persist Basic (Java) ===");

        var s1 = new PersistTest();
        s1.set_value(10);
        s1.go_active();
        s1.set_value(5);

        String json = s1.save_state();
        var data = new org.json.JSONObject(json);
        if (!data.getJSONObject("_compartment").getString("state").equals("Active")) {
            System.out.println("FAIL: Expected Active"); System.exit(1);
        }
        if (data.getInt("value") != 10) {
            System.out.println("FAIL: Expected value 10"); System.exit(1);
        }
        System.out.println("1. Saved: " + json);

        var s2 = PersistTest.restore_state(json);
        if (s2.get_value() != 10) {
            System.out.println("FAIL: Restored value " + s2.get_value()); System.exit(1);
        }
        System.out.println("2. Restored value: " + s2.get_value());

        s2.set_value(3);
        if (s2.get_value() != 6) {
            System.out.println("FAIL: Expected 6, got " + s2.get_value()); System.exit(1);
        }
        System.out.println("3. After set_value(3) in Active: " + s2.get_value());

        s2.go_idle();
        s2.set_value(4);
        if (s2.get_value() != 4) {
            System.out.println("FAIL: Expected 4, got " + s2.get_value()); System.exit(1);
        }
        System.out.println("4. After go_idle, set_value(4): " + s2.get_value());

        System.out.println("PASS: Persist basic works correctly");
    }
}
