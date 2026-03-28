using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class TransitionExitArgsFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public TransitionExitArgsFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public TransitionExitArgsFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class TransitionExitArgsFrameContext {
    public TransitionExitArgsFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public TransitionExitArgsFrameContext(TransitionExitArgsFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class TransitionExitArgsCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public TransitionExitArgsFrameEvent forward_event;
    public TransitionExitArgsCompartment parent_compartment;

    public TransitionExitArgsCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public TransitionExitArgsCompartment Copy() {
        TransitionExitArgsCompartment c = new TransitionExitArgsCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class TransitionExitArgs {
    private List<TransitionExitArgsCompartment> _state_stack;
    private TransitionExitArgsCompartment __compartment;
    private TransitionExitArgsCompartment __next_compartment;
    private List<TransitionExitArgsFrameContext> _context_stack;
    public List<object> log = new List<object>();

    public TransitionExitArgs() {
        _state_stack = new List<TransitionExitArgsCompartment>();
        _context_stack = new List<TransitionExitArgsFrameContext>();
        __compartment = new TransitionExitArgsCompartment("Active");
        __next_compartment = null;
        TransitionExitArgsFrameEvent __frame_event = new TransitionExitArgsFrameEvent("$>");
        TransitionExitArgsFrameContext __ctx = new TransitionExitArgsFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(TransitionExitArgsFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            TransitionExitArgsFrameEvent exit_event = new TransitionExitArgsFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                TransitionExitArgsFrameEvent enter_event = new TransitionExitArgsFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    TransitionExitArgsFrameEvent enter_event = new TransitionExitArgsFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(TransitionExitArgsFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Active") {
            _state_Active(__e);
        } else if (state_name == "Done") {
            _state_Done(__e);
        }
    }

    private void __transition(TransitionExitArgsCompartment next) {
        __next_compartment = next;
    }

    public void leave() {
        TransitionExitArgsFrameEvent __e = new TransitionExitArgsFrameEvent("leave");
        TransitionExitArgsFrameContext __ctx = new TransitionExitArgsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public List<object> get_log() {
        TransitionExitArgsFrameEvent __e = new TransitionExitArgsFrameEvent("get_log");
        TransitionExitArgsFrameContext __ctx = new TransitionExitArgsFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (List<object>) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Active(TransitionExitArgsFrameEvent __e) {
        if (__e._message == "<$") {
            var reason = (string) __compartment.exit_args["0"];
            var code = (int) __compartment.exit_args["1"];
            this.log.Add("exit:" + reason + ":" + code);
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        } else if (__e._message == "leave") {
            this.log.Add("leaving");
            __compartment.exit_args["0"] = "cleanup";
            __compartment.exit_args["1"] = 42;
            { var __new_compartment = new TransitionExitArgsCompartment("Done");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Done(TransitionExitArgsFrameEvent __e) {
        if (__e._message == "$>") {
            this.log.Add("enter:done");
        } else if (__e._message == "get_log") {
            _context_stack[_context_stack.Count - 1]._return = this.log;
            return;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 18: Transition Exit Args ===");
        var s = new TransitionExitArgs();

        // Initial state is Active
        var log = (List<object>)s.get_log();
        if (log.Count != 0) {
            Console.WriteLine("FAIL: Expected empty log, got " + string.Join(", ", log));
            Environment.Exit(1);
        }

        // Leave - should call exit handler with args
        s.leave();
        log = (List<object>)s.get_log();
        if (!log.Contains("leaving")) {
            Console.WriteLine("FAIL: Expected 'leaving' in log, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("exit:cleanup:42")) {
            Console.WriteLine("FAIL: Expected 'exit:cleanup:42' in log, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        if (!log.Contains("enter:done")) {
            Console.WriteLine("FAIL: Expected 'enter:done' in log, got " + string.Join(", ", log));
            Environment.Exit(1);
        }
        Console.WriteLine("Log after transition: [" + string.Join(", ", log) + "]");

        Console.WriteLine("PASS: Transition exit args work correctly");
    }
}
