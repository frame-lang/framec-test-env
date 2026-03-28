using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

class CalculatorFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public CalculatorFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public CalculatorFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class CalculatorFrameContext {
    public CalculatorFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public CalculatorFrameContext(CalculatorFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class CalculatorCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public CalculatorFrameEvent forward_event;
    public CalculatorCompartment parent_compartment;

    public CalculatorCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public CalculatorCompartment Copy() {
        CalculatorCompartment c = new CalculatorCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class Calculator {
    private List<CalculatorCompartment> _state_stack;
    private CalculatorCompartment __compartment;
    private CalculatorCompartment __next_compartment;
    private List<CalculatorFrameContext> _context_stack;
    public int result = 0;

    public Calculator() {
        _state_stack = new List<CalculatorCompartment>();
        _context_stack = new List<CalculatorFrameContext>();
        __compartment = new CalculatorCompartment("Ready");
        __next_compartment = null;
        CalculatorFrameEvent __frame_event = new CalculatorFrameEvent("$>");
        CalculatorFrameContext __ctx = new CalculatorFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(CalculatorFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            CalculatorFrameEvent exit_event = new CalculatorFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                CalculatorFrameEvent enter_event = new CalculatorFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    CalculatorFrameEvent enter_event = new CalculatorFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(CalculatorFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Ready") {
            _state_Ready(__e);
        }
    }

    private void __transition(CalculatorCompartment next) {
        __next_compartment = next;
    }

    public int add(int a, int b) {
        Dictionary<string, object> __params = new Dictionary<string, object>();
        __params["a"] = a;
        __params["b"] = b;
        CalculatorFrameEvent __e = new CalculatorFrameEvent("add", __params);
        CalculatorFrameContext __ctx = new CalculatorFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public int get_result() {
        CalculatorFrameEvent __e = new CalculatorFrameEvent("get_result");
        CalculatorFrameContext __ctx = new CalculatorFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Ready(CalculatorFrameEvent __e) {
        if (__e._message == "add") {
            var a = (int) __e._parameters["a"];
            var b = (int) __e._parameters["b"];
            this.result = a + b;
            _context_stack[_context_stack.Count - 1]._return = this.result;
            return;
        } else if (__e._message == "get_result") {
            _context_stack[_context_stack.Count - 1]._return = this.result;
            return;
        }
    }
}

class CounterFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public CounterFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public CounterFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class CounterFrameContext {
    public CounterFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public CounterFrameContext(CounterFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class CounterCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public CounterFrameEvent forward_event;
    public CounterCompartment parent_compartment;

    public CounterCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public CounterCompartment Copy() {
        CounterCompartment c = new CounterCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class Counter {
    private List<CounterCompartment> _state_stack;
    private CounterCompartment __compartment;
    private CounterCompartment __next_compartment;
    private List<CounterFrameContext> _context_stack;
    public int count = 0;

    public Counter() {
        _state_stack = new List<CounterCompartment>();
        _context_stack = new List<CounterFrameContext>();
        __compartment = new CounterCompartment("Active");
        __next_compartment = null;
        CounterFrameEvent __frame_event = new CounterFrameEvent("$>");
        CounterFrameContext __ctx = new CounterFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(CounterFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            CounterFrameEvent exit_event = new CounterFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                CounterFrameEvent enter_event = new CounterFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    CounterFrameEvent enter_event = new CounterFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(CounterFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    private void __transition(CounterCompartment next) {
        __next_compartment = next;
    }

    public void increment() {
        CounterFrameEvent __e = new CounterFrameEvent("increment");
        CounterFrameContext __ctx = new CounterFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public int get_count() {
        CounterFrameEvent __e = new CounterFrameEvent("get_count");
        CounterFrameContext __ctx = new CounterFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (int) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Active(CounterFrameEvent __e) {
        if (__e._message == "get_count") {
            _context_stack[_context_stack.Count - 1]._return = this.count;
            return;
        } else if (__e._message == "increment") {
            this.count = this.count + 1;
        }
    }
}

class Program {
    static void Main(string[] args) {
        Console.WriteLine("=== Test 39: Tagged System Instantiation ===");

        // Tagged instantiation - validated at transpile time
        var calc = new Calculator();
        var counter = new Counter();

        // Test Calculator
        var result = (int)calc.add(3, 4);
        if (result != 7) {
            Console.WriteLine("FAIL: Expected 7, got " + result);
            Environment.Exit(1);
        }
        Console.WriteLine("Calculator.add(3, 4) = " + result);

        result = (int)calc.get_result();
        if (result != 7) {
            Console.WriteLine("FAIL: Expected 7, got " + result);
            Environment.Exit(1);
        }
        Console.WriteLine("Calculator.get_result() = " + result);

        // Test Counter
        counter.increment();
        counter.increment();
        counter.increment();
        var count = (int)counter.get_count();
        if (count != 3) {
            Console.WriteLine("FAIL: Expected 3, got " + count);
            Environment.Exit(1);
        }
        Console.WriteLine("Counter after 3 increments: " + count);

        Console.WriteLine("PASS: Tagged instantiation works correctly");
    }
}
