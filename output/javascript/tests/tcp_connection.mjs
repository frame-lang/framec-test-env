
// TCP Connection State Machine (simplified RFC 793)
// Two Frame systems â TcpClient and TcpServer â communicating through
// direct method calls simulating packet exchange.

export class TcpServerFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class TcpServerFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class TcpServerCompartment {
    state;
    state_args;
    state_vars;
    enter_args;
    exit_args;
    forward_event;
    parent_compartment;

    constructor(state, parent_compartment = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    copy() {
        const c = new TcpServerCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class TcpServer {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    last_data = "";

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new TcpServerCompartment("Closed");
        this.__next_compartment = null;
        const __frame_event = new TcpServerFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    __kernel(__e) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new TcpServerFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new TcpServerFrameEvent("$>", this.__compartment.enter_args);
                this.__router(enter_event);
            } else {
                // Forward event to new state
                const forward_event = next_compartment.forward_event;
                next_compartment.forward_event = null;
                if (forward_event._message === "$>") {
                    // Forwarding enter event - just send it
                    this.__router(forward_event);
                } else {
                    // Forwarding other event - send $> first, then forward
                    const enter_event = new TcpServerFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    __router(__e) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = this[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    __transition(next_compartment) {
        this.__next_compartment = next_compartment;
    }

    listen() {
        const __e = new TcpServerFrameEvent("listen", null);
        const __ctx = new TcpServerFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    receive_syn() {
        const __e = new TcpServerFrameEvent("receive_syn", null);
        const __ctx = new TcpServerFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    receive_ack() {
        const __e = new TcpServerFrameEvent("receive_ack", null);
        const __ctx = new TcpServerFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    receive_fin() {
        const __e = new TcpServerFrameEvent("receive_fin", null);
        const __ctx = new TcpServerFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    receive_data(data) {
        const __e = new TcpServerFrameEvent("receive_data", {"data": data});
        const __ctx = new TcpServerFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    close() {
        const __e = new TcpServerFrameEvent("close", null);
        const __ctx = new TcpServerFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_state() {
        const __e = new TcpServerFrameEvent("get_state", null);
        const __ctx = new TcpServerFrameContext(__e, null);
        __ctx._return = "Unknown";
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_FinWait2(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "FinWait2";
            return;
        } else if (__e._message === "receive_fin") {
            const __compartment = new TcpServerCompartment("TimeWait", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Closing(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Closing";
            return;
        } else if (__e._message === "receive_ack") {
            const __compartment = new TcpServerCompartment("TimeWait", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Closed(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Closed";
            return;
        } else if (__e._message === "listen") {
            const __compartment = new TcpServerCompartment("Listen", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_CloseWait(__e) {
        if (__e._message === "close") {
            const __compartment = new TcpServerCompartment("LastAck", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "CloseWait";
            return;
        }
    }

    _state_Established(__e) {
        if (__e._message === "close") {
            const __compartment = new TcpServerCompartment("FinWait1", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Established";
            return;
        } else if (__e._message === "receive_data") {
            const data = __e._parameters?.["data"];
            this.last_data = data;
        } else if (__e._message === "receive_fin") {
            const __compartment = new TcpServerCompartment("CloseWait", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_FinWait1(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "FinWait1";
            return;
        } else if (__e._message === "receive_ack") {
            const __compartment = new TcpServerCompartment("FinWait2", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "receive_fin") {
            const __compartment = new TcpServerCompartment("Closing", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Listen(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Listen";
            return;
        } else if (__e._message === "receive_syn") {
            const __compartment = new TcpServerCompartment("SynReceived", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_LastAck(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "LastAck";
            return;
        } else if (__e._message === "receive_ack") {
            const __compartment = new TcpServerCompartment("Closed", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_TimeWait(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "TimeWait";
            return;
        } else if (__e._message === "receive_ack") {
            const __compartment = new TcpServerCompartment("Closed", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_SynReceived(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "SynReceived";
            return;
        } else if (__e._message === "receive_ack") {
            const __compartment = new TcpServerCompartment("Established", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }
}


export class TcpClientFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class TcpClientFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class TcpClientCompartment {
    state;
    state_args;
    state_vars;
    enter_args;
    exit_args;
    forward_event;
    parent_compartment;

    constructor(state, parent_compartment = null) {
        this.state = state;
        this.state_args = {  };
        this.state_vars = {  };
        this.enter_args = {  };
        this.exit_args = {  };
        this.forward_event = null;
        this.parent_compartment = parent_compartment;
    }

    copy() {
        const c = new TcpClientCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class TcpClient {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    sent_count = 0;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new TcpClientCompartment("Closed");
        this.__next_compartment = null;
        const __frame_event = new TcpClientFrameEvent("$>", null);
        this.__kernel(__frame_event);
    }

    __kernel(__e) {
        // Route event to current state
        this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new TcpClientFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new TcpClientFrameEvent("$>", this.__compartment.enter_args);
                this.__router(enter_event);
            } else {
                // Forward event to new state
                const forward_event = next_compartment.forward_event;
                next_compartment.forward_event = null;
                if (forward_event._message === "$>") {
                    // Forwarding enter event - just send it
                    this.__router(forward_event);
                } else {
                    // Forwarding other event - send $> first, then forward
                    const enter_event = new TcpClientFrameEvent("$>", this.__compartment.enter_args);
                    this.__router(enter_event);
                    this.__router(forward_event);
                }
            }
        }
    }

    __router(__e) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = this[handler_name];
        if (handler) {
            handler.call(this, __e);
        }
    }

    __transition(next_compartment) {
        this.__next_compartment = next_compartment;
    }

    connect() {
        const __e = new TcpClientFrameEvent("connect", null);
        const __ctx = new TcpClientFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    receive_syn_ack() {
        const __e = new TcpClientFrameEvent("receive_syn_ack", null);
        const __ctx = new TcpClientFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    receive_ack() {
        const __e = new TcpClientFrameEvent("receive_ack", null);
        const __ctx = new TcpClientFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    receive_fin() {
        const __e = new TcpClientFrameEvent("receive_fin", null);
        const __ctx = new TcpClientFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    send_data(data) {
        const __e = new TcpClientFrameEvent("send_data", {"data": data});
        const __ctx = new TcpClientFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    close() {
        const __e = new TcpClientFrameEvent("close", null);
        const __ctx = new TcpClientFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_state() {
        const __e = new TcpClientFrameEvent("get_state", null);
        const __ctx = new TcpClientFrameContext(__e, null);
        __ctx._return = "Unknown";
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_FinWait2(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "FinWait2";
            return;
        } else if (__e._message === "receive_fin") {
            const __compartment = new TcpClientCompartment("TimeWait", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_FinWait1(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "FinWait1";
            return;
        } else if (__e._message === "receive_ack") {
            const __compartment = new TcpClientCompartment("FinWait2", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "receive_fin") {
            const __compartment = new TcpClientCompartment("Closing", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_LastAck(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "LastAck";
            return;
        } else if (__e._message === "receive_ack") {
            const __compartment = new TcpClientCompartment("Closed", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Established(__e) {
        if (__e._message === "close") {
            const __compartment = new TcpClientCompartment("FinWait1", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Established";
            return;
        } else if (__e._message === "receive_fin") {
            const __compartment = new TcpClientCompartment("CloseWait", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "send_data") {
            const data = __e._parameters?.["data"];
            this.sent_count += 1;
        }
    }

    _state_Closed(__e) {
        if (__e._message === "connect") {
            const __compartment = new TcpClientCompartment("SynSent", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Closed";
            return;
        }
    }

    _state_Closing(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Closing";
            return;
        } else if (__e._message === "receive_ack") {
            const __compartment = new TcpClientCompartment("TimeWait", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_TimeWait(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "TimeWait";
            return;
        } else if (__e._message === "receive_ack") {
            const __compartment = new TcpClientCompartment("Closed", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_SynSent(__e) {
        if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "SynSent";
            return;
        } else if (__e._message === "receive_syn_ack") {
            const __compartment = new TcpClientCompartment("Established", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_CloseWait(__e) {
        if (__e._message === "close") {
            const __compartment = new TcpClientCompartment("LastAck", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "CloseWait";
            return;
        }
    }
}

// ============================================================
// Test Harness
// ============================================================

function assert_state(system, expected, label) {
    const actual = system.get_state();
    if (actual !== expected) {
        console.log(`FAIL: ${label} â expected '${expected}', got '${actual}'`);
        throw new Error(`State assertion failed: ${label}`);
    }
}

function test_happy_path() {
    const server = new TcpServer();
    const client = new TcpClient();

    assert_state(server, "Closed", "server initial");
    assert_state(client, "Closed", "client initial");

    server.listen();
    assert_state(server, "Listen", "server listen");

    client.connect();
    assert_state(client, "SynSent", "client syn sent");

    server.receive_syn();
    assert_state(server, "SynReceived", "server syn received");

    client.receive_syn_ack();
    assert_state(client, "Established", "client established");

    server.receive_ack();
    assert_state(server, "Established", "server established");

    client.send_data("hello");
    server.receive_data("hello");

    client.close();
    assert_state(client, "FinWait1", "client fin wait 1");

    server.receive_fin();
    assert_state(server, "CloseWait", "server close wait");

    client.receive_ack();
    assert_state(client, "FinWait2", "client fin wait 2");

    server.close();
    assert_state(server, "LastAck", "server last ack");

    client.receive_fin();
    assert_state(client, "TimeWait", "client time wait");

    server.receive_ack();
    assert_state(server, "Closed", "server closed");

    client.receive_ack();
    assert_state(client, "Closed", "client closed");

    console.log("PASS: TCP happy path");
}

function test_simultaneous_close() {
    const server = new TcpServer();
    const client = new TcpClient();

    server.listen();
    client.connect();
    server.receive_syn();
    client.receive_syn_ack();
    server.receive_ack();

    client.close();
    server.close();
    assert_state(client, "FinWait1", "client fin wait 1");
    assert_state(server, "FinWait1", "server fin wait 1");

    client.receive_fin();
    server.receive_fin();
    assert_state(client, "Closing", "client closing");
    assert_state(server, "Closing", "server closing");

    client.receive_ack();
    server.receive_ack();
    assert_state(client, "TimeWait", "client time wait");
    assert_state(server, "TimeWait", "server time wait");

    client.receive_ack();
    server.receive_ack();
    assert_state(client, "Closed", "client closed");
    assert_state(server, "Closed", "server closed");

    console.log("PASS: TCP simultaneous close");
}

test_happy_path();
test_simultaneous_close();
console.log("PASS: All TCP connection tests passed");
