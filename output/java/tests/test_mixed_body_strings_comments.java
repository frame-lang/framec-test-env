import java.util.*;


import java.util.*;

class MixedBodyStringsCommentsFrameEvent {
    String _message;
    HashMap<String, Object> _parameters;

    MixedBodyStringsCommentsFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    MixedBodyStringsCommentsFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class MixedBodyStringsCommentsFrameContext {
    MixedBodyStringsCommentsFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    MixedBodyStringsCommentsFrameContext(MixedBodyStringsCommentsFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class MixedBodyStringsCommentsCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    MixedBodyStringsCommentsFrameEvent forward_event;
    MixedBodyStringsCommentsCompartment parent_compartment;

    MixedBodyStringsCommentsCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    MixedBodyStringsCommentsCompartment copy() {
        MixedBodyStringsCommentsCompartment c = new MixedBodyStringsCommentsCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class MixedBodyStringsComments {
    private ArrayList<MixedBodyStringsCommentsCompartment> _state_stack;
    private MixedBodyStringsCommentsCompartment __compartment;
    private MixedBodyStringsCommentsCompartment __next_compartment;
    private ArrayList<MixedBodyStringsCommentsFrameContext> _context_stack;

    public MixedBodyStringsComments() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new MixedBodyStringsCommentsCompartment("Init");
        __next_compartment = null;
        MixedBodyStringsCommentsFrameEvent __frame_event = new MixedBodyStringsCommentsFrameEvent("$>");
        MixedBodyStringsCommentsFrameContext __ctx = new MixedBodyStringsCommentsFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void __kernel(MixedBodyStringsCommentsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            MixedBodyStringsCommentsFrameEvent exit_event = new MixedBodyStringsCommentsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                MixedBodyStringsCommentsFrameEvent enter_event = new MixedBodyStringsCommentsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message.equals("$>")) {
                    __router(forward_event);
                } else {
                    MixedBodyStringsCommentsFrameEvent enter_event = new MixedBodyStringsCommentsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(MixedBodyStringsCommentsFrameEvent __e) {
        String state_name = __compartment.state;
        if (state_name.equals("Init")) {
            _state_Init(__e);
        } else if (state_name.equals("Done")) {
            _state_Done(__e);
        }
    }

    private void __transition(MixedBodyStringsCommentsCompartment next) {
        __next_compartment = next;
    }

    public void start() {
        MixedBodyStringsCommentsFrameEvent __e = new MixedBodyStringsCommentsFrameEvent("start");
        MixedBodyStringsCommentsFrameContext __ctx = new MixedBodyStringsCommentsFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    private void _state_Done(MixedBodyStringsCommentsFrameEvent __e) {

    }

    private void _state_Init(MixedBodyStringsCommentsFrameEvent __e) {
        if (__e._message.equals("start")) {
            // Native Java with Frame-statement-like tokens in strings and comments
            String text = "This mentions -> $Next and pop$ inside a string.";
            // A comment that mentions => $^ and -> $Other should not be parsed as Frame
            System.out.println(text);
            var __compartment = new MixedBodyStringsCommentsCompartment("Done");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }
}

class Main {
    public static void main(String[] args) {
        System.out.println("TAP version 14");
        System.out.println("1..1");
        try {
            MixedBodyStringsComments s = new MixedBodyStringsComments();
            System.out.println("ok 1 - test_mixed_body_strings_comments");
        } catch (Exception ex) {
            System.out.println("not ok 1 - test_mixed_body_strings_comments # " + ex);
        }
    }
}
