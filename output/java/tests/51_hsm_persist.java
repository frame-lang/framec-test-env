import java.util.*;


import java.util.*;

class HSMPersistFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    HSMPersistFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    HSMPersistFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class HSMPersistFrameContext {
    HSMPersistFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    HSMPersistFrameContext(HSMPersistFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class HSMPersistCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    HSMPersistFrameEvent forward_event;
    HSMPersistCompartment parent_compartment;

    HSMPersistCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    HSMPersistCompartment copy() {
        HSMPersistCompartment c = new HSMPersistCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class HSMPersist {
    private ArrayList<HSMPersistCompartment> _state_stack;
    private HSMPersistCompartment __compartment;
    private HSMPersistCompartment __next_compartment;
    private ArrayList<HSMPersistFrameContext> _context_stack;
    public int parent_count_init = 100;

    public HSMPersist() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new HSMPersistCompartment("Parent");
        __next_compartment = null;
        HSMPersistFrameEvent __frame_event = new HSMPersistFrameEvent("$>");
        HSMPersistFrameContext __ctx = new HSMPersistFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
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
                if (forward_event._message.equals("$>")) {
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
        String state_name = __compartment.state;
        if (state_name.equals("Parent")) {
            _state_Parent(__e);
        } else if (state_name.equals("Child")) {
            _state_Child(__e);
        }
    }

    private void __transition(HSMPersistCompartment next) {
        __next_compartment = next;
    }

    public void increment_child() {
        HSMPersistFrameEvent __e = new HSMPersistFrameEvent("increment_child");
        HSMPersistFrameContext __ctx = new HSMPersistFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void increment_parent() {
        HSMPersistFrameEvent __e = new HSMPersistFrameEvent("increment_parent");
        HSMPersistFrameContext __ctx = new HSMPersistFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public int get_child_count() {
        HSMPersistFrameEvent __e = new HSMPersistFrameEvent("get_child_count");
        HSMPersistFrameContext __ctx = new HSMPersistFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public int get_parent_count() {
        HSMPersistFrameEvent __e = new HSMPersistFrameEvent("get_parent_count");
        HSMPersistFrameContext __ctx = new HSMPersistFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (int) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_state() {
        HSMPersistFrameEvent __e = new HSMPersistFrameEvent("get_state");
        HSMPersistFrameContext __ctx = new HSMPersistFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Parent(HSMPersistFrameEvent __e) {
        if (__e._message.equals("get_child_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = -1;
            return;
        } else if (__e._message.equals("get_parent_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = (int) __compartment.state_vars.get("parent_count");
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Parent";
            return;
        } else if (__e._message.equals("increment_child")) {
        } else if (__e._message.equals("increment_parent")) {
            __compartment.state_vars.put("parent_count", (int) __compartment.state_vars.get("parent_count") + 1);
        }
    }

    private void _state_Child(HSMPersistFrameEvent __e) {
        var __sv_comp = __compartment;
        while (__sv_comp != null && !__sv_comp.state.equals("Child")) { __sv_comp = __sv_comp.parent_compartment; }
        if (__e._message.equals("$>")) {
            if (!__sv_comp.state_vars.containsKey("child_count")) {
                __sv_comp.state_vars.put("child_count", 0);
            }
        } else if (__e._message.equals("get_child_count")) {
            _context_stack.get(_context_stack.size() - 1)._return = (int) __sv_comp.state_vars.get("child_count");
            return;
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Child";
            return;
        } else if (__e._message.equals("increment_child")) {
            __sv_comp.state_vars.put("child_count", (int) __sv_comp.state_vars.get("child_count") + 1);
        }
    }

    private org.json.JSONObject __serComp(HSMPersistCompartment comp) {
        if (comp == null) return null;
        var j = new org.json.JSONObject();
        j.put("state", comp.state);
        var sv = new org.json.JSONObject();
        for (var e : comp.state_vars.entrySet()) { sv.put(e.getKey(), e.getValue()); }
        j.put("state_vars", sv);
        j.put("parent", __serComp(comp.parent_compartment));
        return j;
    }

    private static HSMPersistCompartment __deserComp(Object obj) {
        if (obj == null || obj.equals(org.json.JSONObject.NULL)) return null;
        var d = (org.json.JSONObject) obj;
        var c = new HSMPersistCompartment(d.getString("state"));
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
        __j.put("parent_count_init", parent_count_init);
        return __j.toString();
    }

    public static HSMPersist restore_state(String json) {
        var __j = new org.json.JSONObject(json);
        var __instance = new HSMPersist();
        __instance.__compartment = __deserComp(__j.get("_compartment"));
        if (__j.has("_state_stack")) {
            var __stack = __j.getJSONArray("_state_stack");
            __instance._state_stack = new ArrayList<>();
            for (int i = 0; i < __stack.length(); i++) { __instance._state_stack.add(__deserComp(__stack.get(i))); }
        }
        if (__j.has("parent_count_init")) { __instance.parent_count_init = __j.getInt("parent_count_init"); }
        return __instance;
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 51: HSM Persistence (Java) ===");

        // Note: parent_count is a state var on $Parent, init from domain
        // For simplicity, test with child_count state var only
        var s1 = new HSMPersist();
        s1.increment_child();
        s1.increment_child();
        s1.increment_child();

        if (s1.get_child_count() != 3) {
            System.out.println("FAIL: child_count " + s1.get_child_count()); System.exit(1);
        }
        System.out.println("1. child_count: " + s1.get_child_count());

        String json = s1.save_state();
        System.out.println("2. Saved: " + json.length() + " chars");

        var s2 = HSMPersist.restore_state(json);
        if (!s2.get_state().equals("Child")) {
            System.out.println("FAIL: state " + s2.get_state()); System.exit(1);
        }
        System.out.println("3. Restored state: " + s2.get_state());

        if (s2.get_child_count() != 3) {
            System.out.println("FAIL: restored child_count " + s2.get_child_count()); System.exit(1);
        }
        System.out.println("4. child_count preserved: " + s2.get_child_count());

        s2.increment_child();
        if (s2.get_child_count() != 4) {
            System.out.println("FAIL: post-restore " + s2.get_child_count()); System.exit(1);
        }
        System.out.println("5. After increment: " + s2.get_child_count());

        System.out.println("PASS: HSM persistence works correctly");
    }
}
