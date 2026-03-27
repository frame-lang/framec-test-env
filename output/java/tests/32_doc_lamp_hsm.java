import java.util.*;


import java.util.*;

class LampHSMFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    LampHSMFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    LampHSMFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class LampHSMFrameContext {
    LampHSMFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    LampHSMFrameContext(LampHSMFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class LampHSMCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    LampHSMFrameEvent forward_event;
    LampHSMCompartment parent_compartment;

    LampHSMCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    LampHSMCompartment copy() {
        LampHSMCompartment c = new LampHSMCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class LampHSM {
    private ArrayList<LampHSMCompartment> _state_stack;
    private LampHSMCompartment __compartment;
    private LampHSMCompartment __next_compartment;
    private ArrayList<LampHSMFrameContext> _context_stack;
    public String color = "white";
    public boolean lamp_on = false;

    public LampHSM() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        // HSM: Create parent compartment chain
        var __parent_comp_0 = new LampHSMCompartment("ColorBehavior");
        this.__compartment = new LampHSMCompartment("Off");
        this.__compartment.parent_compartment = __parent_comp_0;
        this.__next_compartment = null;
        LampHSMFrameEvent __frame_event = new LampHSMFrameEvent("$>");
        LampHSMFrameContext __ctx = new LampHSMFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
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
                if (forward_event._message.equals("$>")) {
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
        String state_name = __compartment.state;
        if (state_name.equals("Off")) {
            _state_Off(__e);
        } else if (state_name.equals("On")) {
            _state_On(__e);
        } else if (state_name.equals("ColorBehavior")) {
            _state_ColorBehavior(__e);
        }
    }

    private void __transition(LampHSMCompartment next) {
        __next_compartment = next;
    }

    public void turnOn() {
        LampHSMFrameEvent __e = new LampHSMFrameEvent("turnOn");
        LampHSMFrameContext __ctx = new LampHSMFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void turnOff() {
        LampHSMFrameEvent __e = new LampHSMFrameEvent("turnOff");
        LampHSMFrameContext __ctx = new LampHSMFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public String getColor() {
        LampHSMFrameEvent __e = new LampHSMFrameEvent("getColor");
        LampHSMFrameContext __ctx = new LampHSMFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public void setColor(String color) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("color", color);
        LampHSMFrameEvent __e = new LampHSMFrameEvent("setColor", __params);
        LampHSMFrameContext __ctx = new LampHSMFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public boolean isLampOn() {
        LampHSMFrameEvent __e = new LampHSMFrameEvent("isLampOn");
        LampHSMFrameContext __ctx = new LampHSMFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_ColorBehavior(LampHSMFrameEvent __e) {
        if (__e._message.equals("getColor")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.color;
            return;
        } else if (__e._message.equals("setColor")) {
            var color = (String) __e._parameters.get("color");
            this.color = color;
        }
    }

    private void _state_Off(LampHSMFrameEvent __e) {
        if (__e._message.equals("isLampOn")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.lamp_on;
            return;
        } else if (__e._message.equals("turnOn")) {
            var __compartment = new LampHSMCompartment("On");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else {
            _state_ColorBehavior(__e);
        }
    }

    private void _state_On(LampHSMFrameEvent __e) {
        if (__e._message.equals("<$")) {
            this.turnOffLamp();
        } else if (__e._message.equals("$>")) {
            this.turnOnLamp();
        } else if (__e._message.equals("isLampOn")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.lamp_on;
            return;
        } else if (__e._message.equals("turnOff")) {
            var __compartment = new LampHSMCompartment("Off");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        } else {
            _state_ColorBehavior(__e);
        }
    }

    private void turnOnLamp() {
                    this.lamp_on = true;
    }

    private void turnOffLamp() {
                    this.lamp_on = false;
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 32: Doc Lamp HSM ===");
        var lamp = new LampHSM();

        // Color behavior available in both states
        if (!lamp.getColor().equals("white")) {
            System.out.println("FAIL: Expected 'white', got '" + lamp.getColor() + "'");
            System.exit(1);
        }
        lamp.setColor("red");
        if (!lamp.getColor().equals("red")) {
            System.out.println("FAIL: Expected 'red', got '" + lamp.getColor() + "'");
            System.exit(1);
        }

        // Turn on
        lamp.turnOn();
        if (lamp.isLampOn() != true) {
            System.out.println("FAIL: Lamp should be on");
            System.exit(1);
        }

        // Color still works when on
        lamp.setColor("green");
        if (!lamp.getColor().equals("green")) {
            System.out.println("FAIL: Expected 'green', got '" + lamp.getColor() + "'");
            System.exit(1);
        }

        // Turn off
        lamp.turnOff();
        if (lamp.isLampOn() != false) {
            System.out.println("FAIL: Lamp should be off");
            System.exit(1);
        }

        // Color still works when off
        if (!lamp.getColor().equals("green")) {
            System.out.println("FAIL: Expected 'green', got '" + lamp.getColor() + "'");
            System.exit(1);
        }

        System.out.println("PASS: HSM lamp works correctly");
    }
}
