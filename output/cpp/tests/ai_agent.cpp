#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>

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

class AiAgentFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    AiAgentFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class AiAgentFrameContext {
public:
    AiAgentFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    AiAgentFrameContext(AiAgentFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class AiAgentCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<AiAgentFrameEvent> forward_event;
    std::unique_ptr<AiAgentCompartment> parent_compartment;

    explicit AiAgentCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<AiAgentCompartment> clone() const {
        auto c = std::make_unique<AiAgentCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class AiAgent {
private:
    std::vector<std::unique_ptr<AiAgentCompartment>> _state_stack;
    std::unique_ptr<AiAgentCompartment> __compartment;
    std::unique_ptr<AiAgentCompartment> __next_compartment;
    std::vector<AiAgentFrameContext> _context_stack;

    void __kernel(AiAgentFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            AiAgentFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                AiAgentFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    AiAgentFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(AiAgentFrameEvent& __e) {
        const auto& state_name = __compartment->state;
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

    void __transition(std::unique_ptr<AiAgentCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Flee(AiAgentFrameEvent& __e) {
        if (__e._message == "$>") {
            action_log = action_log + "flee,";
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Flee"));
            return;
        } else if (__e._message == "tick") {
            // Precondition: still low health?
            if (health >= 20) {
                // Condition no longer met -- back to root for re-evaluation
                auto __new_compartment = std::make_unique<AiAgentCompartment>("Root");
                __new_compartment->parent_compartment = __compartment->clone();
                __transition(std::move(__new_compartment));
                return;
            }

            // Action: flee (increase distance, recover health)
            enemy_distance = enemy_distance + 10;
            health = health + 5;
            action_log = action_log + "flee,";
        }
    }

    void _state_Attack(AiAgentFrameEvent& __e) {
        if (__e._message == "$>") {
            action_log = action_log + "attack,";
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Attack"));
            return;
        } else if (__e._message == "tick") {
            // Survival interrupt
            if (health < 20) {
                auto __new_compartment = std::make_unique<AiAgentCompartment>("Flee");
                __new_compartment->parent_compartment = __compartment->clone();
                __transition(std::move(__new_compartment));
                return;
            }

            // Precondition: still in range?
            if (enemy_distance > 5) {
                // Enemy moved away -- go back to approach
                auto __new_compartment = std::make_unique<AiAgentCompartment>("Approach");
                __new_compartment->parent_compartment = __compartment->clone();
                __transition(std::move(__new_compartment));
                return;
            }

            // Precondition: enemy still alive?
            if (enemy_health <= 0) {
                // Victory -- back to idle
                enemy_distance = 100;
                auto __new_compartment = std::make_unique<AiAgentCompartment>("Root");
                __new_compartment->parent_compartment = __compartment->clone();
                __transition(std::move(__new_compartment));
                return;
            }

            // Action: attack
            enemy_health = enemy_health - 25;
            action_log = action_log + "attack,";
        }
    }

    void _state_Approach(AiAgentFrameEvent& __e) {
        if (__e._message == "$>") {
            action_log = action_log + "approach,";
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Approach"));
            return;
        } else if (__e._message == "tick") {
            // Survival interrupt: flee takes priority
            if (health < 20) {
                auto __new_compartment = std::make_unique<AiAgentCompartment>("Flee");
                __new_compartment->parent_compartment = __compartment->clone();
                __transition(std::move(__new_compartment));
                return;
            }

            // Precondition: enemy still visible?
            if (enemy_distance >= 50) {
                auto __new_compartment = std::make_unique<AiAgentCompartment>("Root");
                __new_compartment->parent_compartment = __compartment->clone();
                __transition(std::move(__new_compartment));
                return;
            }

            // Action: move closer
            if (enemy_distance > 5) {
                enemy_distance = enemy_distance - 10;
                action_log = action_log + "approach,";
            } else {
                // In range -- sequence continues to Attack
                auto __new_compartment = std::make_unique<AiAgentCompartment>("Attack");
                __new_compartment->parent_compartment = __compartment->clone();
                __transition(std::move(__new_compartment));
                return;
            }
        }
    }

    void _state_Patrol(AiAgentFrameEvent& __e) {
        if (__e._message == "$>") {
            action_log = action_log + "patrol,";
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Patrol"));
            return;
        } else if (__e._message == "tick") {
            // Higher-priority interrupt: combat
            if (enemy_distance < 50) {
                auto __new_compartment = std::make_unique<AiAgentCompartment>("Approach");
                __new_compartment->parent_compartment = __compartment->clone();
                __transition(std::move(__new_compartment));
                return;
            }

            // Higher-priority interrupt: survival
            if (health < 20) {
                auto __new_compartment = std::make_unique<AiAgentCompartment>("Flee");
                __new_compartment->parent_compartment = __compartment->clone();
                __transition(std::move(__new_compartment));
                return;
            }

            // Action: patrol
            patrol_step = patrol_step + 1;
            action_log = action_log + "patrol,";
        }
    }

    void _state_Root(AiAgentFrameEvent& __e) {
        if (__e._message == "$>") {
            action_log = "";
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("Root"));
            return;
        } else if (__e._message == "tick") {
            // Selector: check conditions in priority order
            if (health < 20) {
                auto __new_compartment = std::make_unique<AiAgentCompartment>("Flee");
                __new_compartment->parent_compartment = __compartment->clone();
                __transition(std::move(__new_compartment));
                return;
            }
            if (enemy_distance < 50) {
                auto __new_compartment = std::make_unique<AiAgentCompartment>("Approach");
                __new_compartment->parent_compartment = __compartment->clone();
                __transition(std::move(__new_compartment));
                return;
            }
            auto __new_compartment = std::make_unique<AiAgentCompartment>("Patrol");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

public:
    int health = 100;
    int enemy_distance = 100;
    int enemy_health = 100;
    int patrol_step = 0;
    std::string action_log = "";

    AiAgent() {
        __compartment = std::make_unique<AiAgentCompartment>("Root");
        AiAgentFrameEvent __frame_event("$>");
        AiAgentFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void tick() {
        AiAgentFrameEvent __e("tick");
        AiAgentFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string get_state() {
        AiAgentFrameEvent __e("get_state");
        AiAgentFrameContext __ctx(std::move(__e), std::any(std::string("Unknown")));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string get_action_log() {
        AiAgentFrameEvent __e("get_action_log");
        AiAgentFrameContext __ctx(std::move(__e), std::any(std::string("")));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void set_health(int v) {
         health = v; 
    }

    void set_enemy_distance(int v) {
         enemy_distance = v; 
    }

    void set_enemy_health(int v) {
         enemy_health = v; 
    }
};


// ============================================================
// Test Harness
// ============================================================

void assert_state(AiAgent& agent, const std::string& expected, const std::string& label) {
    auto actual = agent.get_state();
    if (actual != expected) {
        printf("FAIL: %s â expected '%s', got '%s'\n", label.c_str(), expected.c_str(), actual.c_str());
        assert(false && "State assertion failed");
    }
}

void test_priority_interrupt() {
    AiAgent agent;

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

    printf("PASS: BT priority interrupt\n");
}

void test_sequence_completion() {
    AiAgent agent;

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

    printf("PASS: BT sequence completion\n");
}

void test_re_evaluation() {
    AiAgent agent;

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

    printf("PASS: BT re-evaluation\n");
}

int main() {
    test_priority_interrupt();
    test_sequence_completion();
    test_re_evaluation();
    printf("PASS: All behavior tree tests passed\n");
    return 0;
}
