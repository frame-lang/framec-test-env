using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class MixedBodyStringsCommentsFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public MixedBodyStringsCommentsFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public MixedBodyStringsCommentsFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class MixedBodyStringsCommentsFrameContext {
    public MixedBodyStringsCommentsFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public MixedBodyStringsCommentsFrameContext(MixedBodyStringsCommentsFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class MixedBodyStringsCommentsCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public MixedBodyStringsCommentsFrameEvent forward_event;
    public MixedBodyStringsCommentsCompartment parent_compartment;

    public MixedBodyStringsCommentsCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public MixedBodyStringsCommentsCompartment Copy() {
        MixedBodyStringsCommentsCompartment c = new MixedBodyStringsCommentsCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class MixedBodyStringsComments {
    private List<MixedBodyStringsCommentsCompartment> _state_stack;
    private MixedBodyStringsCommentsCompartment __compartment;
    private MixedBodyStringsCommentsCompartment __next_compartment;
    private List<MixedBodyStringsCommentsFrameContext> _context_stack;

    public MixedBodyStringsComments() {
        _state_stack = new List<MixedBodyStringsCommentsCompartment>();
        _context_stack = new List<MixedBodyStringsCommentsFrameContext>();
        __compartment = new MixedBodyStringsCommentsCompartment("Init");
        __next_compartment = null;
        MixedBodyStringsCommentsFrameEvent __frame_event = new MixedBodyStringsCommentsFrameEvent("$>");
        MixedBodyStringsCommentsFrameContext __ctx = new MixedBodyStringsCommentsFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
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
                if (forward_event._message == "$>") {
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
        string state_name = __compartment.state;
        if (state_name == "Init") {
            _state_Init(__e);
        } else if (state_name == "Done") {
            _state_Done(__e);
        }
    }

    private void __transition(MixedBodyStringsCommentsCompartment next) {
        __next_compartment = next;
    }

    public void start() {
        MixedBodyStringsCommentsFrameEvent __e = new MixedBodyStringsCommentsFrameEvent("start");
        MixedBodyStringsCommentsFrameContext __ctx = new MixedBodyStringsCommentsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void _state_Init(MixedBodyStringsCommentsFrameEvent __e) {
        if (__e._message == "start") {
            // Native C# with Frame-statement-like tokens in strings and comments
            string text = "This mentions -> $Next and pop$ inside a string.";
            // A comment that mentions => $^ and -> $Other should not be parsed as Frame
            Console.WriteLine(text);
            { var __new_compartment = new MixedBodyStringsCommentsCompartment("Done");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Done(MixedBodyStringsCommentsFrameEvent __e) {

    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("TAP version 14");
        Console.WriteLine("1..1");
        try {
            MixedBodyStringsComments s = new MixedBodyStringsComments();
            Console.WriteLine("ok 1 - test_mixed_body_strings_comments");
        } catch (Exception ex) {
            Console.WriteLine("not ok 1 - test_mixed_body_strings_comments # " + ex);
        }
    }
}
