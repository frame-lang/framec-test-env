
// Test 9: Two async systems interacting
// Validates: multiple async systems in one file

async function mockGenerate() {
    await Promise.resolve();
    return "raw_data";
}

async function mockProcess(data) {
    await Promise.resolve();
    return "processed:" + data;
}

export class AsyncProducerFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class AsyncProducerFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class AsyncProducerCompartment {
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
        const c = new AsyncProducerCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class AsyncProducer {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new AsyncProducerCompartment("Ready");
        this.__next_compartment = null;
    }

    async __kernel(__e) {
        // Route event to current state
        await this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new AsyncProducerFrameEvent("<$", this.__compartment.exit_args);
            await this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new AsyncProducerFrameEvent("$>", this.__compartment.enter_args);
                await this.__router(enter_event);
            } else {
                // Forward event to new state
                const forward_event = next_compartment.forward_event;
                next_compartment.forward_event = null;
                if (forward_event._message === "$>") {
                    // Forwarding enter event - just send it
                    await this.__router(forward_event);
                } else {
                    // Forwarding other event - send $> first, then forward
                    const enter_event = new AsyncProducerFrameEvent("$>", this.__compartment.enter_args);
                    await this.__router(enter_event);
                    await this.__router(forward_event);
                }
            }
        }
    }

    async __router(__e) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = this[handler_name];
        if (handler) {
            await handler.call(this, __e);
        }
    }

    __transition(next_compartment) {
        this.__next_compartment = next_compartment;
    }

    async produce() {
        const __e = new AsyncProducerFrameEvent("produce", null);
        const __ctx = new AsyncProducerFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async _state_Ready(__e) {
        if (__e._message === "produce") {
            const data = await mockGenerate()
            this._context_stack[this._context_stack.length - 1]._return = data;
            return;
        }
    }

    async init() {
        const __e = new AsyncProducerFrameEvent("$>", null);
        const __ctx = new AsyncProducerFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }
}

export class AsyncConsumerFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class AsyncConsumerFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class AsyncConsumerCompartment {
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
        const c = new AsyncConsumerCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class AsyncConsumer {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    last_result = "";

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new AsyncConsumerCompartment("Waiting");
        this.__next_compartment = null;
    }

    async __kernel(__e) {
        // Route event to current state
        await this.__router(__e);
        // Process any pending transition
        while (this.__next_compartment !== null) {
            const next_compartment = this.__next_compartment;
            this.__next_compartment = null;
            // Exit current state
            const exit_event = new AsyncConsumerFrameEvent("<$", this.__compartment.exit_args);
            await this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new AsyncConsumerFrameEvent("$>", this.__compartment.enter_args);
                await this.__router(enter_event);
            } else {
                // Forward event to new state
                const forward_event = next_compartment.forward_event;
                next_compartment.forward_event = null;
                if (forward_event._message === "$>") {
                    // Forwarding enter event - just send it
                    await this.__router(forward_event);
                } else {
                    // Forwarding other event - send $> first, then forward
                    const enter_event = new AsyncConsumerFrameEvent("$>", this.__compartment.enter_args);
                    await this.__router(enter_event);
                    await this.__router(forward_event);
                }
            }
        }
    }

    async __router(__e) {
        const state_name = this.__compartment.state;
        const handler_name = `_state_${state_name}`;
        const handler = this[handler_name];
        if (handler) {
            await handler.call(this, __e);
        }
    }

    __transition(next_compartment) {
        this.__next_compartment = next_compartment;
    }

    async consume(data) {
        const __e = new AsyncConsumerFrameEvent("consume", {"data": data});
        const __ctx = new AsyncConsumerFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }

    async get_result() {
        const __e = new AsyncConsumerFrameEvent("get_result", null);
        const __ctx = new AsyncConsumerFrameContext(__e, null);
        __ctx._return = "";
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    async _state_Done(__e) {
        if (__e._message === "get_result") {
            this._context_stack[this._context_stack.length - 1]._return = this.last_result;
            return;
        }
    }

    async _state_Waiting(__e) {
        if (__e._message === "consume") {
            const data = __e._parameters?.["data"];
            const processed = await mockProcess(data)
            this.last_result = processed
            const __compartment = new AsyncConsumerCompartment("Done", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        } else if (__e._message === "get_result") {
            this._context_stack[this._context_stack.length - 1]._return = this.last_result;
            return;
        }
    }

    async init() {
        const __e = new AsyncConsumerFrameEvent("$>", null);
        const __ctx = new AsyncConsumerFrameContext(__e, null);
        this._context_stack.push(__ctx);
        await this.__kernel(__e);
        this._context_stack.pop();
    }
}

async function main() {
    let producer = new AsyncProducer();
    let consumer = new AsyncConsumer();
    await producer.init();
    await consumer.init();

    // Producer generates data
    let data = await producer.produce();
    if (data !== "raw_data") {
        throw new Error(`produce: expected 'raw_data', got '${data}'`);
    }

    // Consumer processes it
    await consumer.consume(data);
    let result = await consumer.get_result();
    if (result !== "processed:raw_data") {
        throw new Error(`consume: expected 'processed:raw_data', got '${result}'`);
    }

    console.log("PASS: async multi-system â two async systems interact correctly");
}

main();
