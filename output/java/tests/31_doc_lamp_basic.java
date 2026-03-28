import java.util.*;


import java.util.*;

class LampFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    LampFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    LampFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class LampFrameContext {
    LampFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    LampFrameContext(LampFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class LampCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    LampFrameEvent forward_event;
    LampCompartment parent_compartment;

    LampCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    LampCompartment copy() {
        LampCompartment c = new LampCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class Lamp {
    private ArrayList<LampCompartment> _state_stack;
    private LampCompartment __compartment;
    private LampCompartment __next_compartment;
    private ArrayList<LampFrameContext> _context_stack;
    public String color = "white";
    public boolean switch_closed = false;

    public Lamp() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new LampCompartment("Off");
        __next_compartment = null;
        LampFrameEvent __frame_event = new LampFrameEvent("$>");
        LampFrameContext __ctx = new LampFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(LampFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            LampFrameEvent exit_event = new LampFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                LampFrameEvent enter_event = new LampFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    LampFrameEvent enter_event = new LampFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(LampFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Off")) {
            _state_Off(__e);
        } else if (state_name.equals("On")) {
            _state_On(__e);
        }
    }

    private void __transition(LampCompartment next) {
        __next_compartment = next;
    }

    public void turnOn() {
        LampFrameEvent __e = new LampFrameEvent("turnOn");
        LampFrameContext __ctx = new LampFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public void turnOff() {
        LampFrameEvent __e = new LampFrameEvent("turnOff");
        LampFrameContext __ctx = new LampFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public String getColor() {
        LampFrameEvent __e = new LampFrameEvent("getColor");
        LampFrameContext __ctx = new LampFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public void setColor(String color) {
        HashMap<String, Object> __params = new HashMap<>();
        __params.put("color", color);
        LampFrameEvent __e = new LampFrameEvent("setColor", __params);
        LampFrameContext __ctx = new LampFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public boolean isSwitchClosed() {
        LampFrameEvent __e = new LampFrameEvent("isSwitchClosed");
        LampFrameContext __ctx = new LampFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (boolean) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_On(LampFrameEvent __e) {
        if (__e._message.equals("<$")) {
            this.openSwitch();
        } else if (__e._message.equals("$>")) {
            this.closeSwitch();
        } else if (__e._message.equals("getColor")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.color;
            return;
        } else if (__e._message.equals("isSwitchClosed")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.switch_closed;
            return;
        } else if (__e._message.equals("setColor")) {
            var color = (String) __e._parameters.get("color");
            this.color = color;
        } else if (__e._message.equals("turnOff")) {
            var __compartment = new LampCompartment("Off");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Off(LampFrameEvent __e) {
        if (__e._message.equals("getColor")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.color;
            return;
        } else if (__e._message.equals("isSwitchClosed")) {
            _context_stack.get(_context_stack.size() - 1)._return = this.switch_closed;
            return;
        } else if (__e._message.equals("setColor")) {
            var color = (String) __e._parameters.get("color");
            this.color = color;
        } else if (__e._message.equals("turnOn")) {
            var __compartment = new LampCompartment("On");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void closeSwitch() {
                    this.switch_closed = true;
    }

    private void openSwitch() {
                    this.switch_closed = false;
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 31: Doc Lamp Basic ===");
        var lamp = new Lamp();

        // Initially off
        if (lamp.isSwitchClosed() != false) {
            System.out.println("FAIL: Switch should be open initially");
            System.exit(1);
        }

        // Turn on - should close switch
        lamp.turnOn();
        if (lamp.isSwitchClosed() != true) {
            System.out.println("FAIL: Switch should be closed after turnOn");
            System.exit(1);
        }

        // Check color
        if (!lamp.getColor().equals("white")) {
            System.out.println("FAIL: Expected 'white', got '" + lamp.getColor() + "'");
            System.exit(1);
        }

        // Set color
        lamp.setColor("blue");
        if (!lamp.getColor().equals("blue")) {
            System.out.println("FAIL: Expected 'blue', got '" + lamp.getColor() + "'");
            System.exit(1);
        }

        // Turn off - should open switch
        lamp.turnOff();
        if (lamp.isSwitchClosed() != false) {
            System.out.println("FAIL: Switch should be open after turnOff");
            System.exit(1);
        }

        System.out.println("PASS: Basic lamp works correctly");
    }
}
