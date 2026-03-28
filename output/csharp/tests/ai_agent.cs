using System;
using System.Collections.Generic;


using System;
using System.Collections.Generic;

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

class AiAgentFrameEvent {
    public string _message;
    public Dictionary<string, object> _parameters;

    public AiAgentFrameEvent(string message) {
        this._message = message;
        this._parameters = null;
    }

    public AiAgentFrameEvent(string message, Dictionary<string, object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class AiAgentFrameContext {
    public AiAgentFrameEvent _event;
    public object _return;
    public Dictionary<string, object> _data;

    public AiAgentFrameContext(AiAgentFrameEvent ev, object defaultReturn) {
        this._event = ev;
        this._return = defaultReturn;
        this._data = new Dictionary<string, object>();
    }
}

class AiAgentCompartment {
    public string state;
    public Dictionary<string, object> state_args;
    public Dictionary<string, object> state_vars;
    public Dictionary<string, object> enter_args;
    public Dictionary<string, object> exit_args;
    public AiAgentFrameEvent forward_event;
    public AiAgentCompartment parent_compartment;

    public AiAgentCompartment(string state) {
        this.state = state;
        this.state_args = new Dictionary<string, object>();
        this.state_vars = new Dictionary<string, object>();
        this.enter_args = new Dictionary<string, object>();
        this.exit_args = new Dictionary<string, object>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    public AiAgentCompartment Copy() {
        AiAgentCompartment c = new AiAgentCompartment(this.state);
        c.state_args = new Dictionary<string, object>(this.state_args);
        c.state_vars = new Dictionary<string, object>(this.state_vars);
        c.enter_args = new Dictionary<string, object>(this.enter_args);
        c.exit_args = new Dictionary<string, object>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class AiAgent {
    private List<AiAgentCompartment> _state_stack;
    private AiAgentCompartment __compartment;
    private AiAgentCompartment __next_compartment;
    private List<AiAgentFrameContext> _context_stack;
    public int health = 100;
    public int enemy_distance = 100;
    public int enemy_health = 100;
    public int patrol_step = 0;
    public string action_log = "";

    public AiAgent() {
        _state_stack = new List<AiAgentCompartment>();
        _context_stack = new List<AiAgentFrameContext>();
        __compartment = new AiAgentCompartment("Root");
        __next_compartment = null;
        AiAgentFrameEvent __frame_event = new AiAgentFrameEvent("$>");
        AiAgentFrameContext __ctx = new AiAgentFrameContext(__frame_event, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    private void __kernel(AiAgentFrameEvent __e) {
        __router(__e);
        while (__next_compartment != null) {
            var next_compartment = __next_compartment;
            __next_compartment = null;
            AiAgentFrameEvent exit_event = new AiAgentFrameEvent("<$");
            __router(exit_event);
            __compartment = next_compartment;
            if (__compartment.forward_event == null) {
                AiAgentFrameEvent enter_event = new AiAgentFrameEvent("$>");
                __router(enter_event);
            } else {
                var forward_event = __compartment.forward_event;
                __compartment.forward_event = null;
                if (forward_event._message == "$>") {
                    __router(forward_event);
                } else {
                    AiAgentFrameEvent enter_event = new AiAgentFrameEvent("$>");
                    __router(enter_event);
                    __router(forward_event);
                }
            }
        }
    }

    private void __router(AiAgentFrameEvent __e) {
        string state_name = __compartment.state;
        if (state_name == "Root") {
            _state_Root(__e);
        } else if (state_name == "Flee") {
            _state_Flee(__e);
        } else if (state_name == "Approach") {
            _state_Approach(__e);
        } else if (state_name == "Attack") {
            _state_Attack(__e);
        } else if (state_name == "Patrol") {
            _state_Patrol(__e);
        }
    }

    private void __transition(AiAgentCompartment next) {
        __next_compartment = next;
    }

    public void tick() {
        AiAgentFrameEvent __e = new AiAgentFrameEvent("tick");
        AiAgentFrameContext __ctx = new AiAgentFrameContext(__e, null);
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        _context_stack.RemoveAt(_context_stack.Count - 1);
    }

    public string get_state() {
        AiAgentFrameEvent __e = new AiAgentFrameEvent("get_state");
        AiAgentFrameContext __ctx = new AiAgentFrameContext(__e, "Unknown");
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    public string get_action_log() {
        AiAgentFrameEvent __e = new AiAgentFrameEvent("get_action_log");
        AiAgentFrameContext __ctx = new AiAgentFrameContext(__e, "");
        _context_stack.Add(__ctx);
        __kernel(_context_stack[_context_stack.Count - 1]._event);
        var __result = (string) _context_stack[_context_stack.Count - 1]._return;
        _context_stack.RemoveAt(_context_stack.Count - 1);
        return __result;
    }

    private void _state_Flee(AiAgentFrameEvent __e) {
        if (__e._message == "$>") {
            this.action_log = this.action_log + "flee,";
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Flee";
            return;
        } else if (__e._message == "tick") {
            // Precondition: still low health?
            if (this.health >= 20) {
                { var __new_compartment = new AiAgentCompartment("Root");
                __new_compartment.parent_compartment = __compartment.Copy();
                __transition(__new_compartment); }
                return;
            }

            // Action: flee (increase distance, recover health)
            this.enemy_distance = this.enemy_distance + 10;
            this.health = this.health + 5;
            this.action_log = this.action_log + "flee,";
        }
    }

    private void _state_Root(AiAgentFrameEvent __e) {
        if (__e._message == "$>") {
            this.action_log = "";
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Root";
            return;
        } else if (__e._message == "tick") {
            // Selector: check conditions in priority order
            if (this.health < 20) {
                { var __new_compartment = new AiAgentCompartment("Flee");
                __new_compartment.parent_compartment = __compartment.Copy();
                __transition(__new_compartment); }
                return;
            }
            if (this.enemy_distance < 50) {
                { var __new_compartment = new AiAgentCompartment("Approach");
                __new_compartment.parent_compartment = __compartment.Copy();
                __transition(__new_compartment); }
                return;
            }
            { var __new_compartment = new AiAgentCompartment("Patrol");
            __new_compartment.parent_compartment = __compartment.Copy();
            __transition(__new_compartment); }
            return;
        }
    }

    private void _state_Attack(AiAgentFrameEvent __e) {
        if (__e._message == "$>") {
            this.action_log = this.action_log + "attack,";
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Attack";
            return;
        } else if (__e._message == "tick") {
            // Survival interrupt
            if (this.health < 20) {
                { var __new_compartment = new AiAgentCompartment("Flee");
                __new_compartment.parent_compartment = __compartment.Copy();
                __transition(__new_compartment); }
                return;
            }

            // Precondition: still in range?
            if (this.enemy_distance > 5) {
                { var __new_compartment = new AiAgentCompartment("Approach");
                __new_compartment.parent_compartment = __compartment.Copy();
                __transition(__new_compartment); }
                return;
            }

            // Precondition: enemy still alive?
            if (this.enemy_health <= 0) {
                this.enemy_distance = 100;
                { var __new_compartment = new AiAgentCompartment("Root");
                __new_compartment.parent_compartment = __compartment.Copy();
                __transition(__new_compartment); }
                return;
            }

            // Action: attack
            this.enemy_health = this.enemy_health - 25;
            this.action_log = this.action_log + "attack,";
        }
    }

    private void _state_Patrol(AiAgentFrameEvent __e) {
        if (__e._message == "$>") {
            this.action_log = this.action_log + "patrol,";
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Patrol";
            return;
        } else if (__e._message == "tick") {
            // Higher-priority interrupt: combat
            if (this.enemy_distance < 50) {
                { var __new_compartment = new AiAgentCompartment("Approach");
                __new_compartment.parent_compartment = __compartment.Copy();
                __transition(__new_compartment); }
                return;
            }

            // Higher-priority interrupt: survival
            if (this.health < 20) {
                { var __new_compartment = new AiAgentCompartment("Flee");
                __new_compartment.parent_compartment = __compartment.Copy();
                __transition(__new_compartment); }
                return;
            }

            // Action: patrol
            this.patrol_step = this.patrol_step + 1;
            this.action_log = this.action_log + "patrol,";
        }
    }

    private void _state_Approach(AiAgentFrameEvent __e) {
        if (__e._message == "$>") {
            this.action_log = this.action_log + "approach,";
        } else if (__e._message == "get_state") {
            _context_stack[_context_stack.Count - 1]._return = "Approach";
            return;
        } else if (__e._message == "tick") {
            // Survival interrupt: flee takes priority
            if (this.health < 20) {
                { var __new_compartment = new AiAgentCompartment("Flee");
                __new_compartment.parent_compartment = __compartment.Copy();
                __transition(__new_compartment); }
                return;
            }

            // Precondition: enemy still visible?
            if (this.enemy_distance >= 50) {
                { var __new_compartment = new AiAgentCompartment("Root");
                __new_compartment.parent_compartment = __compartment.Copy();
                __transition(__new_compartment); }
                return;
            }

            // Action: move closer
            if (this.enemy_distance > 5) {
                this.enemy_distance = this.enemy_distance - 10;
                this.action_log = this.action_log + "approach,";
            } else {
                // In range -- sequence continues to Attack
                { var __new_compartment = new AiAgentCompartment("Attack");
                __new_compartment.parent_compartment = __compartment.Copy();
                __transition(__new_compartment); }
                return;
            }
        }
    }

    public void set_health(int v) {
         this.health = v; 
    }

    public void set_enemy_distance(int v) {
         this.enemy_distance = v; 
    }

    public void set_enemy_health(int v) {
         this.enemy_health = v; 
    }
}


// ============================================================
// Test Harness
// ============================================================

class Program {
    static void assert_state(AiAgent agent, string expected, string label) {
        string actual = (string) agent.get_state();
        if (actual != expected) {
            Console.WriteLine("FAIL: " + label + " -- expected '" + expected + "', got '" + actual + "'");
            throw new Exception("State assertion failed: " + label);
        }
    }

    static void test_priority_interrupt() {
        AiAgent agent = new AiAgent();

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

        Console.WriteLine("PASS: BT priority interrupt");
    }

    static void test_sequence_completion() {
        AiAgent agent = new AiAgent();

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

        Console.WriteLine("PASS: BT sequence completion");
    }

    static void test_re_evaluation() {
        AiAgent agent = new AiAgent();

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

        Console.WriteLine("PASS: BT re-evaluation");
    }

    static void Main(string[] args) {
        try {
            test_priority_interrupt();
            test_sequence_completion();
            test_re_evaluation();
            Console.WriteLine("PASS: All behavior tree tests passed");
        } catch (Exception ex) {
            Console.WriteLine("FAIL: " + ex.Message);
            Environment.Exit(1);
        }
    }
}
