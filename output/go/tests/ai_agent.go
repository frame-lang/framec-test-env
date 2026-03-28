
package main

import (
	"fmt"
	"os"
)

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

type AiAgentFrameEvent struct {
    _message    string
    _parameters map[string]any
}

type AiAgentFrameContext struct {
    _event  AiAgentFrameEvent
    _return any
    _data   map[string]any
}

type AiAgentCompartment struct {
    state            string
    stateArgs        map[string]any
    stateVars        map[string]any
    enterArgs        map[string]any
    exitArgs         map[string]any
    forwardEvent     *AiAgentFrameEvent
    parentCompartment *AiAgentCompartment
}

func newAiAgentCompartment(state string) *AiAgentCompartment {
    return &AiAgentCompartment{
        state:    state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
    }
}

func (c *AiAgentCompartment) copy() *AiAgentCompartment {
    nc := &AiAgentCompartment{
        state: c.state,
        stateArgs: make(map[string]any),
        stateVars: make(map[string]any),
        enterArgs: make(map[string]any),
        exitArgs:  make(map[string]any),
        forwardEvent:     c.forwardEvent,
        parentCompartment: c.parentCompartment,
    }
    for k, v := range c.stateArgs { nc.stateArgs[k] = v }
    for k, v := range c.stateVars { nc.stateVars[k] = v }
    for k, v := range c.enterArgs { nc.enterArgs[k] = v }
    for k, v := range c.exitArgs { nc.exitArgs[k] = v }
    return nc
}

type AiAgent struct {
    _state_stack []*AiAgentCompartment
    __compartment *AiAgentCompartment
    __next_compartment *AiAgentCompartment
    _context_stack []AiAgentFrameContext
    health int
    enemy_distance int
    enemy_health int
    patrol_step int
    action_log string
}

func NewAiAgent() *AiAgent {
    s := &AiAgent{}
    s._state_stack = make([]*AiAgentCompartment, 0)
    s._context_stack = make([]AiAgentFrameContext, 0)
    s.__compartment = newAiAgentCompartment("Root")
    s.__next_compartment = nil
    __frame_event := AiAgentFrameEvent{_message: "$>", _parameters: nil}
    __ctx := AiAgentFrameContext{_event: __frame_event, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return s
}

func (s *AiAgent) __kernel(__e *AiAgentFrameEvent) {
    s.__router(__e)
    for s.__next_compartment != nil {
        next_compartment := s.__next_compartment
        s.__next_compartment = nil
        exit_event := &AiAgentFrameEvent{_message: "<$", _parameters: s.__compartment.exitArgs}
        s.__router(exit_event)
        s.__compartment = next_compartment
        if s.__compartment.forwardEvent == nil {
            enter_event := &AiAgentFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
            s.__router(enter_event)
        } else {
            forward_event := s.__compartment.forwardEvent
            s.__compartment.forwardEvent = nil
            if forward_event._message == "$>" {
                s.__router(forward_event)
            } else {
                enter_event := &AiAgentFrameEvent{_message: "$>", _parameters: s.__compartment.enterArgs}
                s.__router(enter_event)
                s.__router(forward_event)
            }
        }
    }
}

func (s *AiAgent) __router(__e *AiAgentFrameEvent) {
    switch s.__compartment.state {
    case "Root":
        s._state_Root(__e)
    case "Flee":
        s._state_Flee(__e)
    case "Approach":
        s._state_Approach(__e)
    case "Attack":
        s._state_Attack(__e)
    case "Patrol":
        s._state_Patrol(__e)
    }
}

func (s *AiAgent) __transition(next *AiAgentCompartment) {
    s.__next_compartment = next
}

func (s *AiAgent) Tick() {
    __e := AiAgentFrameEvent{_message: "Tick"}
    __ctx := AiAgentFrameContext{_event: __e, _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
}

func (s *AiAgent) GetState() string {
    __e := AiAgentFrameEvent{_message: "GetState"}
    __ctx := AiAgentFrameContext{_event: __e, _return: "Unknown", _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *AiAgent) GetActionLog() string {
    __e := AiAgentFrameEvent{_message: "GetActionLog"}
    __ctx := AiAgentFrameContext{_event: __e, _return: "", _data: make(map[string]any)}
    s._context_stack = append(s._context_stack, __ctx)
    s.__kernel(&s._context_stack[len(s._context_stack)-1]._event)
    var __result string
    if __rv := s._context_stack[len(s._context_stack)-1]._return; __rv != nil { __result = __rv.(string) }
    s._context_stack = s._context_stack[:len(s._context_stack)-1]
    return __result
}

func (s *AiAgent) _state_Approach(__e *AiAgentFrameEvent) {
    if __e._message == "$>" {
        s.action_log = s.action_log + "approach,"
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Approach"
        return
    } else if __e._message == "Tick" {
        // Survival interrupt: flee takes priority
        if s.health < 20 {
            __compartment := newAiAgentCompartment("Flee")
            __compartment.parentCompartment = s.__compartment.copy()
            s.__transition(__compartment)
            return
        }

        // Precondition: enemy still visible?
        if s.enemy_distance >= 50 {
            __compartment := newAiAgentCompartment("Root")
            __compartment.parentCompartment = s.__compartment.copy()
            s.__transition(__compartment)
            return
        }

        // Action: move closer
        if s.enemy_distance > 5 {
            s.enemy_distance = s.enemy_distance - 10
            s.action_log = s.action_log + "approach,"
        } else {
            // In range -- sequence continues to Attack
            __compartment := newAiAgentCompartment("Attack")
            __compartment.parentCompartment = s.__compartment.copy()
            s.__transition(__compartment)
            return
        }
    }
}

func (s *AiAgent) _state_Patrol(__e *AiAgentFrameEvent) {
    if __e._message == "$>" {
        s.action_log = s.action_log + "patrol,"
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Patrol"
        return
    } else if __e._message == "Tick" {
        // Higher-priority interrupt: combat
        if s.enemy_distance < 50 {
            __compartment := newAiAgentCompartment("Approach")
            __compartment.parentCompartment = s.__compartment.copy()
            s.__transition(__compartment)
            return
        }

        // Higher-priority interrupt: survival
        if s.health < 20 {
            __compartment := newAiAgentCompartment("Flee")
            __compartment.parentCompartment = s.__compartment.copy()
            s.__transition(__compartment)
            return
        }

        // Action: patrol
        s.patrol_step = s.patrol_step + 1
        s.action_log = s.action_log + "patrol,"
    }
}

func (s *AiAgent) _state_Flee(__e *AiAgentFrameEvent) {
    if __e._message == "$>" {
        s.action_log = s.action_log + "flee,"
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Flee"
        return
    } else if __e._message == "Tick" {
        // Precondition: still low health?
        if s.health >= 20 {
            __compartment := newAiAgentCompartment("Root")
            __compartment.parentCompartment = s.__compartment.copy()
            s.__transition(__compartment)
            return
        }

        // Action: flee (increase distance, recover health)
        s.enemy_distance = s.enemy_distance + 10
        s.health = s.health + 5
        s.action_log = s.action_log + "flee,"
    }
}

func (s *AiAgent) _state_Root(__e *AiAgentFrameEvent) {
    if __e._message == "$>" {
        s.action_log = ""
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Root"
        return
    } else if __e._message == "Tick" {
        // Selector: check conditions in priority order
        if s.health < 20 {
            __compartment := newAiAgentCompartment("Flee")
            __compartment.parentCompartment = s.__compartment.copy()
            s.__transition(__compartment)
            return
        }
        if s.enemy_distance < 50 {
            __compartment := newAiAgentCompartment("Approach")
            __compartment.parentCompartment = s.__compartment.copy()
            s.__transition(__compartment)
            return
        }
        __compartment := newAiAgentCompartment("Patrol")
        __compartment.parentCompartment = s.__compartment.copy()
        s.__transition(__compartment)
        return
    }
}

func (s *AiAgent) _state_Attack(__e *AiAgentFrameEvent) {
    if __e._message == "$>" {
        s.action_log = s.action_log + "attack,"
    } else if __e._message == "GetState" {
        s._context_stack[len(s._context_stack)-1]._return = "Attack"
        return
    } else if __e._message == "Tick" {
        // Survival interrupt
        if s.health < 20 {
            __compartment := newAiAgentCompartment("Flee")
            __compartment.parentCompartment = s.__compartment.copy()
            s.__transition(__compartment)
            return
        }

        // Precondition: still in range?
        if s.enemy_distance > 5 {
            __compartment := newAiAgentCompartment("Approach")
            __compartment.parentCompartment = s.__compartment.copy()
            s.__transition(__compartment)
            return
        }

        // Precondition: enemy still alive?
        if s.enemy_health <= 0 {
            s.enemy_distance = 100
            __compartment := newAiAgentCompartment("Root")
            __compartment.parentCompartment = s.__compartment.copy()
            s.__transition(__compartment)
            return
        }

        // Action: attack
        s.enemy_health = s.enemy_health - 25
        s.action_log = s.action_log + "attack,"
    }
}

func (s *AiAgent) SetHealth(v int) {
     s.health = v 
}

func (s *AiAgent) SetEnemyDistance(v int) {
     s.enemy_distance = v 
}

func (s *AiAgent) SetEnemyHealth(v int) {
     s.enemy_health = v 
}


// ============================================================
// Test Harness
// ============================================================

func assertState(agent *AiAgent, expected string, label string) {
	actual := agent.GetState()
	if actual != expected {
		fmt.Printf("FAIL: %s -- expected '%s', got '%s'\n", label, expected, actual)
		os.Exit(1)
	}
}

func testPriorityInterrupt() {
	agent := NewAiAgent()
	agent.SetHealth(100)
	agent.SetEnemyDistance(100)
	agent.SetEnemyHealth(100)

	// No enemy, full health -> should patrol
	agent.Tick()
	assertState(agent, "Patrol", "initial patrol")

	// Enemy appears at distance 30 -> should approach
	agent.SetEnemyDistance(30)
	agent.Tick()
	assertState(agent, "Approach", "enemy triggers approach")

	// Health drops critically -> should flee (interrupts combat)
	agent.SetHealth(10)
	agent.Tick()
	assertState(agent, "Flee", "low health interrupts combat")

	// Health recovers -> flee transitions to root, then next tick re-evaluates
	agent.SetHealth(50)
	agent.SetEnemyDistance(20)
	agent.Tick() // Flee sees health OK -> transitions to Root
	assertState(agent, "Root", "flee exits to root")
	agent.Tick() // Root re-evaluates -> enemy near -> approach
	assertState(agent, "Approach", "health recovered, back to combat")

	fmt.Println("PASS: BT priority interrupt")
}

func testSequenceCompletion() {
	agent := NewAiAgent()
	agent.SetHealth(100)
	agent.SetEnemyDistance(100)
	agent.SetEnemyHealth(100)

	// Enemy at distance 30
	agent.SetEnemyDistance(30)
	agent.Tick()
	assertState(agent, "Approach", "start approach")

	// Tick: approach reduces distance
	agent.Tick()
	assertState(agent, "Approach", "still approaching")

	// Tick: now close enough (distance <= 5) -> transitions to Attack
	agent.SetEnemyDistance(5)
	agent.Tick()
	assertState(agent, "Attack", "in range, attacking")

	// Tick: attack deals damage
	agent.Tick()
	assertState(agent, "Attack", "still attacking")

	// Enemy dies -> Attack transitions to Root
	agent.SetEnemyHealth(0)
	agent.Tick()
	assertState(agent, "Root", "enemy dead, back to root")
	agent.Tick() // Root re-evaluates -> no enemy -> patrol
	assertState(agent, "Patrol", "enemy dead, patrol")

	fmt.Println("PASS: BT sequence completion")
}

func testReEvaluation() {
	agent := NewAiAgent()
	agent.SetHealth(100)
	agent.SetEnemyDistance(100)
	agent.SetEnemyHealth(100)

	// Enemy at distance 30 -> approach
	agent.SetEnemyDistance(30)
	agent.Tick()
	assertState(agent, "Approach", "approaching")

	// Enemy runs away (distance > 50) -> back to root, then patrol
	agent.SetEnemyDistance(60)
	agent.Tick() // Approach sees no enemy -> Root
	assertState(agent, "Root", "enemy fled, root")
	agent.Tick() // Root -> patrol
	assertState(agent, "Patrol", "enemy fled, patrol")

	// Enemy comes back
	agent.SetEnemyDistance(10)
	agent.Tick()
	assertState(agent, "Approach", "enemy back, approach again")

	fmt.Println("PASS: BT re-evaluation")
}

func main() {
	testPriorityInterrupt()
	testSequenceCompletion()
	testReEvaluation()
	fmt.Println("PASS: All behavior tree tests passed")
}
