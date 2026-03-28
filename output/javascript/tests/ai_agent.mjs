
// Behavior Tree implemented as HSM with tick-driven re-evaluation.
//
// Tree structure (Selector = priority-ordered, Sequence = ordered steps):
//
//   $Root (Selector)
//   +-- $Survival (Selector -- highest priority)
//   |   +-- $Flee (Action -- flee when health < 20)
//   +-- $Combat (Sequence)
//   |   +-- $Approach (Action -- move toward enemy)
//   |   +-- $Attack (Action -- attack when in range)
//   +-- $Idle (Selector -- lowest priority)
//       +-- $Patrol (Action -- walk patrol route)
//
// On every tick:
//   - Root checks conditions top-down (priority)
//   - Transitions to highest-priority subtree whose condition is met
//   - Leaf states check their preconditions each tick and => $^ if invalid
//   - Domain vars act as blackboard

export class AiAgentFrameEvent {
    _message;
    _parameters;

    constructor(message, parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}


export class AiAgentFrameContext {
    event;
    _return;
    _data;

    constructor(event, default_return) {
        this.event = event;
        this._return = default_return;
        this._data = {  };
    }
}


export class AiAgentCompartment {
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
        const c = new AiAgentCompartment(this.state, this.parent_compartment);
        c.state_args = {...this.state_args};
        c.state_vars = {...this.state_vars};
        c.enter_args = {...this.enter_args};
        c.exit_args = {...this.exit_args};
        c.forward_event = this.forward_event;
        return c;
    }
}


export class AiAgent {
    _state_stack;
    __compartment;
    __next_compartment;
    _context_stack;
    health = 100;
    enemy_distance = 100;
    enemy_health = 100;
    patrol_step = 0;
    action_log = "";

    constructor() {
        this._state_stack = [];
        this._context_stack = [];
        this.__compartment = new AiAgentCompartment("Root");
        this.__next_compartment = null;
        const __frame_event = new AiAgentFrameEvent("$>", null);
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
            const exit_event = new AiAgentFrameEvent("<$", this.__compartment.exit_args);
            this.__router(exit_event);
            // Switch to new compartment
            this.__compartment = next_compartment;
            // Enter new state (or forward event)
            if (next_compartment.forward_event === null) {
                const enter_event = new AiAgentFrameEvent("$>", this.__compartment.enter_args);
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
                    const enter_event = new AiAgentFrameEvent("$>", this.__compartment.enter_args);
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

    tick() {
        const __e = new AiAgentFrameEvent("tick", null);
        const __ctx = new AiAgentFrameContext(__e, null);
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        this._context_stack.pop();
    }

    get_state() {
        const __e = new AiAgentFrameEvent("get_state", null);
        const __ctx = new AiAgentFrameContext(__e, null);
        __ctx._return = "Unknown";
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    get_action_log() {
        const __e = new AiAgentFrameEvent("get_action_log", null);
        const __ctx = new AiAgentFrameContext(__e, null);
        __ctx._return = "";
        this._context_stack.push(__ctx);
        this.__kernel(__e);
        return this._context_stack.pop()._return;
    }

    _state_Root(__e) {
        if (__e._message === "$>") {
            this.action_log = "";
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Root";
            return;
        } else if (__e._message === "tick") {
            // Selector: check conditions in priority order
            if (this.health < 20) {
                const __compartment = new AiAgentCompartment("Flee", this.__compartment.copy());
                this.__transition(__compartment);
                return;
            }
            if (this.enemy_distance < 50) {
                const __compartment = new AiAgentCompartment("Approach", this.__compartment.copy());
                this.__transition(__compartment);
                return;
            }
            const __compartment = new AiAgentCompartment("Patrol", this.__compartment.copy());
            this.__transition(__compartment);
            return;
        }
    }

    _state_Attack(__e) {
        if (__e._message === "$>") {
            this.action_log = this.action_log + "attack,";
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Attack";
            return;
        } else if (__e._message === "tick") {
            // Survival interrupt
            if (this.health < 20) {
                const __compartment = new AiAgentCompartment("Flee", this.__compartment.copy());
                this.__transition(__compartment);
                return;
            }

            // Precondition: still in range?
            if (this.enemy_distance > 5) {
                // Enemy moved away -- go back to approach
                const __compartment = new AiAgentCompartment("Approach", this.__compartment.copy());
                this.__transition(__compartment);
                return;
            }

            // Precondition: enemy still alive?
            if (this.enemy_health <= 0) {
                // Victory -- back to idle
                this.enemy_distance = 100;
                const __compartment = new AiAgentCompartment("Root", this.__compartment.copy());
                this.__transition(__compartment);
                return;
            }

            // Action: attack
            this.enemy_health = this.enemy_health - 25;
            this.action_log = this.action_log + "attack,";
        }
    }

    _state_Approach(__e) {
        if (__e._message === "$>") {
            this.action_log = this.action_log + "approach,";
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Approach";
            return;
        } else if (__e._message === "tick") {
            // Survival interrupt: flee takes priority
            if (this.health < 20) {
                const __compartment = new AiAgentCompartment("Flee", this.__compartment.copy());
                this.__transition(__compartment);
                return;
            }

            // Precondition: enemy still visible?
            if (this.enemy_distance >= 50) {
                const __compartment = new AiAgentCompartment("Root", this.__compartment.copy());
                this.__transition(__compartment);
                return;
            }

            // Action: move closer
            if (this.enemy_distance > 5) {
                this.enemy_distance = this.enemy_distance - 10;
                this.action_log = this.action_log + "approach,";
            } else {
                // In range -- sequence continues to Attack
                const __compartment = new AiAgentCompartment("Attack", this.__compartment.copy());
                this.__transition(__compartment);
                return;
            }
        }
    }

    _state_Patrol(__e) {
        if (__e._message === "$>") {
            this.action_log = this.action_log + "patrol,";
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Patrol";
            return;
        } else if (__e._message === "tick") {
            // Higher-priority interrupt: combat
            if (this.enemy_distance < 50) {
                const __compartment = new AiAgentCompartment("Approach", this.__compartment.copy());
                this.__transition(__compartment);
                return;
            }

            // Higher-priority interrupt: survival
            if (this.health < 20) {
                const __compartment = new AiAgentCompartment("Flee", this.__compartment.copy());
                this.__transition(__compartment);
                return;
            }

            // Action: patrol
            this.patrol_step = this.patrol_step + 1;
            this.action_log = this.action_log + "patrol,";
        }
    }

    _state_Flee(__e) {
        if (__e._message === "$>") {
            this.action_log = this.action_log + "flee,";
        } else if (__e._message === "get_state") {
            this._context_stack[this._context_stack.length - 1]._return = "Flee";
            return;
        } else if (__e._message === "tick") {
            // Precondition: still low health?
            if (this.health >= 20) {
                // Condition no longer met -- back to root for re-evaluation
                const __compartment = new AiAgentCompartment("Root", this.__compartment.copy());
                this.__transition(__compartment);
                return;
            }

            // Action: flee (increase distance, recover health)
            this.enemy_distance = this.enemy_distance + 10;
            this.health = this.health + 5;
            this.action_log = this.action_log + "flee,";
        }
    }

    set_health(v) {
         this.health = v; 
    }

    set_enemy_distance(v) {
         this.enemy_distance = v; 
    }

    set_enemy_health(v) {
         this.enemy_health = v; 
    }
}


// ============================================================
// Test Harness
// ============================================================

function assert_state(agent, expected, label) {
    const actual = agent.get_state();
    if (actual !== expected) {
        console.log(`FAIL: ${label} â expected '${expected}', got '${actual}'`);
        throw new Error(`State assertion failed: ${label}`);
    }
}

function test_priority_interrupt() {
    const agent = new AiAgent();

    // No enemy, full health -> should patrol
    agent.tick();
    assert_state(agent, "Patrol", "initial patrol");

    // Enemy appears at distance 30 -> should approach
    agent.set_enemy_distance(30);
    agent.tick();
    assert_state(agent, "Approach", "enemy triggers approach");

    // Health drops critically -> should flee (interrupts combat)
    agent.set_health(10);
    agent.tick();
    assert_state(agent, "Flee", "low health interrupts combat");

    // Health recovers -> flee transitions to root, then next tick re-evaluates
    agent.set_health(50);
    agent.set_enemy_distance(20);
    agent.tick();  // Flee sees health OK -> transitions to Root
    assert_state(agent, "Root", "flee exits to root");
    agent.tick();  // Root re-evaluates -> enemy near -> approach
    assert_state(agent, "Approach", "health recovered, back to combat");

    console.log("PASS: BT priority interrupt");
}

function test_sequence_completion() {
    const agent = new AiAgent();

    // Enemy at distance 30
    agent.set_enemy_distance(30);
    agent.tick();
    assert_state(agent, "Approach", "start approach");

    // Tick: approach reduces distance
    agent.tick();
    assert_state(agent, "Approach", "still approaching");

    // Tick: now close enough (distance <= 5) -> transitions to Attack
    agent.set_enemy_distance(5);
    agent.tick();
    assert_state(agent, "Attack", "in range, attacking");

    // Tick: attack deals damage
    agent.tick();
    assert_state(agent, "Attack", "still attacking");

    // Enemy dies -> Attack transitions to Root
    agent.set_enemy_health(0);
    agent.tick();
    assert_state(agent, "Root", "enemy dead, back to root");
    agent.tick();  // Root re-evaluates -> no enemy -> patrol
    assert_state(agent, "Patrol", "enemy dead, patrol");

    console.log("PASS: BT sequence completion");
}

function test_re_evaluation() {
    const agent = new AiAgent();

    // Enemy at distance 30 -> approach
    agent.set_enemy_distance(30);
    agent.tick();
    assert_state(agent, "Approach", "approaching");

    // Enemy runs away (distance > 50) -> back to root, then patrol
    agent.set_enemy_distance(60);
    agent.tick();  // Approach sees no enemy -> Root
    assert_state(agent, "Root", "enemy fled, root");
    agent.tick();  // Root -> patrol
    assert_state(agent, "Patrol", "enemy fled, patrol");

    // Enemy comes back
    agent.set_enemy_distance(10);
    agent.tick();
    assert_state(agent, "Approach", "enemy back, approach again");

    console.log("PASS: BT re-evaluation");
}

test_priority_interrupt();
test_sequence_completion();
test_re_evaluation();
console.log("PASS: All behavior tree tests passed");
