import java.util.*;


import java.util.*;

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
    String _message;
    HashMap<String, Object> _parameters;

    AiAgentFrameEvent(String message) {
        this._message = message;
        this._parameters = null;
    }

    AiAgentFrameEvent(String message, HashMap<String, Object> parameters) {
        this._message = message;
        this._parameters = parameters;
    }
}

class AiAgentFrameContext {
    AiAgentFrameEvent _event;
    Object _return;
    HashMap<String, Object> _data;

    AiAgentFrameContext(AiAgentFrameEvent event, Object defaultReturn) {
        this._event = event;
        this._return = defaultReturn;
        this._data = new HashMap<>();
    }
}

class AiAgentCompartment {
    String state;
    HashMap<String, Object> state_args;
    HashMap<String, Object> state_vars;
    HashMap<String, Object> enter_args;
    HashMap<String, Object> exit_args;
    AiAgentFrameEvent forward_event;
    AiAgentCompartment parent_compartment;

    AiAgentCompartment(String state) {
        this.state = state;
        this.state_args = new HashMap<>();
        this.state_vars = new HashMap<>();
        this.enter_args = new HashMap<>();
        this.exit_args = new HashMap<>();
        this.forward_event = null;
        this.parent_compartment = null;
    }

    AiAgentCompartment copy() {
        AiAgentCompartment c = new AiAgentCompartment(this.state);
        c.state_args = new HashMap<>(this.state_args);
        c.state_vars = new HashMap<>(this.state_vars);
        c.enter_args = new HashMap<>(this.enter_args);
        c.exit_args = new HashMap<>(this.exit_args);
        c.forward_event = this.forward_event;
        c.parent_compartment = this.parent_compartment;
        return c;
    }
}

class AiAgent {
    private ArrayList<AiAgentCompartment> _state_stack;
    private AiAgentCompartment __compartment;
    private AiAgentCompartment __next_compartment;
    private ArrayList<AiAgentFrameContext> _context_stack;
    public int health = 100;
    public int enemy_distance = 100;
    public int enemy_health = 100;
    public int patrol_step = 0;
    public String action_log = "";

    public AiAgent() {
        _state_stack = new ArrayList<>();
        _context_stack = new ArrayList<>();
        __compartment = new AiAgentCompartment("Root");
        __next_compartment = null;
        AiAgentFrameEvent __frame_event = new AiAgentFrameEvent("$>");
        AiAgentFrameContext __ctx = new AiAgentFrameContext(__frame_event, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
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
                if (forward_event._message.equals("$>")) {
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
        String state_name = __compartment.state;
        if (state_name.equals("Root")) {
            _state_Root(__e);
        } else if (state_name.equals("Flee")) {
            _state_Flee(__e);
        } else if (state_name.equals("Approach")) {
            _state_Approach(__e);
        } else if (state_name.equals("Attack")) {
            _state_Attack(__e);
        } else if (state_name.equals("Patrol")) {
            _state_Patrol(__e);
        }
    }

    private void __transition(AiAgentCompartment next) {
        __next_compartment = next;
    }

    public void tick() {
        AiAgentFrameEvent __e = new AiAgentFrameEvent("tick");
        AiAgentFrameContext __ctx = new AiAgentFrameContext(__e, null);
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        _context_stack.remove(_context_stack.size() - 1);
    }

    public String get_state() {
        AiAgentFrameEvent __e = new AiAgentFrameEvent("get_state");
        AiAgentFrameContext __ctx = new AiAgentFrameContext(__e, "Unknown");
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    public String get_action_log() {
        AiAgentFrameEvent __e = new AiAgentFrameEvent("get_action_log");
        AiAgentFrameContext __ctx = new AiAgentFrameContext(__e, "");
        _context_stack.add(__ctx);
        __kernel(_context_stack.get(_context_stack.size() - 1)._event);
        var __result = (String) _context_stack.get(_context_stack.size() - 1)._return;
        _context_stack.remove(_context_stack.size() - 1);
        return __result;
    }

    private void _state_Root(AiAgentFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.action_log = "";
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Root";
            return;
        } else if (__e._message.equals("tick")) {
            // Selector: check conditions in priority order
            if (this.health < 20) {
                var __compartment = new AiAgentCompartment("Flee");
                __compartment.parent_compartment = this.__compartment.copy();
                __transition(__compartment);
                return;
            }
            if (this.enemy_distance < 50) {
                var __compartment = new AiAgentCompartment("Approach");
                __compartment.parent_compartment = this.__compartment.copy();
                __transition(__compartment);
                return;
            }
            var __compartment = new AiAgentCompartment("Patrol");
            __compartment.parent_compartment = this.__compartment.copy();
            __transition(__compartment);
            return;
        }
    }

    private void _state_Attack(AiAgentFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.action_log = this.action_log + "attack,";
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Attack";
            return;
        } else if (__e._message.equals("tick")) {
            // Survival interrupt
            if (this.health < 20) {
                var __compartment = new AiAgentCompartment("Flee");
                __compartment.parent_compartment = this.__compartment.copy();
                __transition(__compartment);
                return;
            }

            // Precondition: still in range?
            if (this.enemy_distance > 5) {
                var __compartment = new AiAgentCompartment("Approach");
                __compartment.parent_compartment = this.__compartment.copy();
                __transition(__compartment);
                return;
            }

            // Precondition: enemy still alive?
            if (this.enemy_health <= 0) {
                this.enemy_distance = 100;
                var __compartment = new AiAgentCompartment("Root");
                __compartment.parent_compartment = this.__compartment.copy();
                __transition(__compartment);
                return;
            }

            // Action: attack
            this.enemy_health = this.enemy_health - 25;
            this.action_log = this.action_log + "attack,";
        }
    }

    private void _state_Patrol(AiAgentFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.action_log = this.action_log + "patrol,";
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Patrol";
            return;
        } else if (__e._message.equals("tick")) {
            // Higher-priority interrupt: combat
            if (this.enemy_distance < 50) {
                var __compartment = new AiAgentCompartment("Approach");
                __compartment.parent_compartment = this.__compartment.copy();
                __transition(__compartment);
                return;
            }

            // Higher-priority interrupt: survival
            if (this.health < 20) {
                var __compartment = new AiAgentCompartment("Flee");
                __compartment.parent_compartment = this.__compartment.copy();
                __transition(__compartment);
                return;
            }

            // Action: patrol
            this.patrol_step = this.patrol_step + 1;
            this.action_log = this.action_log + "patrol,";
        }
    }

    private void _state_Flee(AiAgentFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.action_log = this.action_log + "flee,";
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Flee";
            return;
        } else if (__e._message.equals("tick")) {
            // Precondition: still low health?
            if (this.health >= 20) {
                var __compartment = new AiAgentCompartment("Root");
                __compartment.parent_compartment = this.__compartment.copy();
                __transition(__compartment);
                return;
            }

            // Action: flee (increase distance, recover health)
            this.enemy_distance = this.enemy_distance + 10;
            this.health = this.health + 5;
            this.action_log = this.action_log + "flee,";
        }
    }

    private void _state_Approach(AiAgentFrameEvent __e) {
        if (__e._message.equals("$>")) {
            this.action_log = this.action_log + "approach,";
        } else if (__e._message.equals("get_state")) {
            _context_stack.get(_context_stack.size() - 1)._return = "Approach";
            return;
        } else if (__e._message.equals("tick")) {
            // Survival interrupt: flee takes priority
            if (this.health < 20) {
                var __compartment = new AiAgentCompartment("Flee");
                __compartment.parent_compartment = this.__compartment.copy();
                __transition(__compartment);
                return;
            }

            // Precondition: enemy still visible?
            if (this.enemy_distance >= 50) {
                var __compartment = new AiAgentCompartment("Root");
                __compartment.parent_compartment = this.__compartment.copy();
                __transition(__compartment);
                return;
            }

            // Action: move closer
            if (this.enemy_distance > 5) {
                this.enemy_distance = this.enemy_distance - 10;
                this.action_log = this.action_log + "approach,";
            } else {
                // In range -- sequence continues to Attack
                var __compartment = new AiAgentCompartment("Attack");
                __compartment.parent_compartment = this.__compartment.copy();
                __transition(__compartment);
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

class Main {
    static void assert_state(AiAgent agent, String expected, String label) throws Exception {
        String actual = (String) agent.get_state();
        if (!actual.equals(expected)) {
            System.out.println("FAIL: " + label + " -- expected '" + expected + "', got '" + actual + "'");
            throw new Exception("State assertion failed: " + label);
        }
    }

    static void test_priority_interrupt() throws Exception {
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

        System.out.println("PASS: BT priority interrupt");
    }

    static void test_sequence_completion() throws Exception {
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

        System.out.println("PASS: BT sequence completion");
    }

    static void test_re_evaluation() throws Exception {
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

        System.out.println("PASS: BT re-evaluation");
    }

    public static void main(String[] args) {
        try {
            test_priority_interrupt();
            test_sequence_completion();
            test_re_evaluation();
            System.out.println("PASS: All behavior tree tests passed");
        } catch (Exception ex) {
            System.out.println("FAIL: " + ex.getMessage());
            System.exit(1);
        }
    }
}
