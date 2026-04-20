# HSM (Hierarchical State Machine) Comprehensive Test Plan

**Version:** 1.0
**Date:** February 2026
**Status:** Draft - Test Plan Only (no test files created yet)

---

## Overview

This document outlines a comprehensive test plan for HSM (Hierarchical State Machine) functionality in Frame V4. The tests are organized by category and cover all aspects of HSM syntax and behavior.

### Existing HSM Tests (Reference)

The following HSM-related tests already exist in the test suite:

| File | Coverage |
|------|----------|
| `08_hsm.fpy` | Basic in-handler `=> $^` forward |
| `30_hsm_default_forward.fpy` | State-level default `=> $^` |
| `32_doc_lamp_hsm.fpy` | Multiple children sharing parent, shared behavior |
| `34_doc_history_hsm.fpy` | HSM with push$/pop$ history |
| `40_hsm_parent_state_vars.fpy` | Parent state variables via forward |

### Test Naming Convention

New tests should follow the pattern: `4X_hsm_<category>_<feature>.fpy`

Starting from `41_` to continue the primary test sequence.

---

## 1. HSM Structure Tests

### 1.1 Single Parent Relationship (`41_hsm_single_parent.fpy`)

**Objective:** Verify basic child-parent relationship syntax and structure.

```
Hierarchy: $Child => $Parent
```

**Test Cases:**
- TC1.1.1: Child declares parent with `=> $Parent` syntax
- TC1.1.2: Child can forward events to parent
- TC1.1.3: Child remains the current state (no transition occurs on forward)
- TC1.1.4: Parent handler executes and returns control

**Verification:**
- Log shows child handler executed first, then parent handler
- State remains $Child after forward

---

### 1.2 Multi-Level Hierarchy (`42_hsm_three_levels.fpy`)

**Objective:** Verify 3+ level deep hierarchies work correctly.

```
Hierarchy: $Grandchild => $Child => $Parent
```

**Test Cases:**
- TC1.2.1: Three-level hierarchy compiles
- TC1.2.2: Forward from grandchild to child works
- TC1.2.3: Forward from grandchild through child to parent works
- TC1.2.4: Each level can handle or forward independently

**Verification:**
- Event forwarded through all three levels executes handlers in order
- Each level's state variables remain isolated

---

### 1.3 Multiple Children of Same Parent (`43_hsm_multi_children.fpy`)

**Objective:** Verify multiple states can share the same parent.

```
Hierarchy:
  $ChildA => $Parent
  $ChildB => $Parent
  $ChildC => $Parent
```

**Test Cases:**
- TC1.3.1: Multiple children can declare same parent
- TC1.3.2: Each child can forward to the shared parent
- TC1.3.3: Transitioning between siblings preserves parent relationship
- TC1.3.4: Each sibling maintains independent state

**Verification:**
- All children can call parent handlers via `=> $^`
- Sibling transitions work correctly

---

### 1.4 Sibling Transitions (`44_hsm_sibling_transitions.fpy`)

**Objective:** Verify transitions between states sharing the same parent.

```
Hierarchy:
  $A => $Parent
  $B => $Parent

Transitions: $A -> $B -> $A
```

**Test Cases:**
- TC1.4.1: Transition from one sibling to another
- TC1.4.2: Exit handler fires on source sibling
- TC1.4.3: Enter handler fires on target sibling
- TC1.4.4: Parent relationship preserved after transition

**Verification:**
- Enter/exit sequence: A:<$, B:$>
- Both siblings still forward to parent correctly after transitions

---

## 2. Enter/Exit Handler Tests

### 2.1 Enter in Child Only (`45_hsm_enter_child_only.fpy`)

**Objective:** Child has `$>()`, parent does not.

```frame
$Child => $Parent {
    $>() { log("Child enter") }
}
$Parent {
    // No enter handler
}
```

**Test Cases:**
- TC2.1.1: Child enter handler fires on entry
- TC2.1.2: No error when parent lacks enter handler
- TC2.1.3: Forward to parent works without parent having enter

---

### 2.2 Enter in Parent Only (`46_hsm_enter_parent_only.fpy`)

**Objective:** Parent has `$>()`, child does not.

```frame
$Child => $Parent {
    // No enter handler
}
$Parent {
    $>() { log("Parent enter") }
}
```

**Test Cases:**
- TC2.2.1: Child enters without error (no enter handler)
- TC2.2.2: Parent's enter does NOT auto-fire when child is entered
- TC2.2.3: Parent enter only fires when transitioning directly TO parent

---

### 2.3 Enter in Both - Signature Matching (`47_hsm_enter_both.fpy`)

**Objective:** Both child and parent have enter handlers.

```frame
$Child => $Parent {
    $>() { log("Child enter") }
}
$Parent {
    $>() { log("Parent enter") }
}
```

**Test Cases:**
- TC2.3.1: Only child's enter fires when entering child
- TC2.3.2: Parent's enter fires only when transitioning to parent
- TC2.3.3: No implicit cascading of enter handlers

---

### 2.4 Exit Handlers (`48_hsm_exit_handlers.fpy`)

**Objective:** Test exit handlers in HSM context.

```frame
$Child => $Parent {
    <$() { log("Child exit") }
}
$Parent {
    <$() { log("Parent exit") }
}
```

**Test Cases:**
- TC2.4.1: Child exit fires when transitioning out of child
- TC2.4.2: Parent exit does NOT fire when transitioning out of child
- TC2.4.3: Exit handler can access child's state variables

---

### 2.5 Enter/Exit with Parameters (`49_hsm_enter_exit_params.fpy`)

**Objective:** Enter and exit handlers with parameters in HSM context.

```frame
$Child => $Parent {
    $>(msg: str) { log(msg) }
    <$(reason: str) { log(reason) }

    go() {
        ("leaving") -> ("arriving") $Sibling
    }
}
```

**Test Cases:**
- TC2.5.1: Exit params passed correctly
- TC2.5.2: Enter params passed to target state
- TC2.5.3: `@@` context available in enter/exit handlers

---

### 2.6 Omitted Handlers - Inherited Behavior (`50_hsm_omitted_handlers.fpy`)

**Objective:** Verify behavior when handlers are omitted at various levels.

**Test Cases:**
- TC2.6.1: Event not handled in child, not forwarded = silent ignore
- TC2.6.2: Event not handled in child, forwarded with `=> $^` = parent handles
- TC2.6.3: State-level `=> $^` forwards all unhandled events

---

## 3. State Variable Tests

### 3.1 State Variables in Child Only (`51_hsm_state_vars_child.fpy`)

**Objective:** Child has state variables, parent does not.

```frame
$Child => $Parent {
    $.count: int = 0

    inc() { $.count = $.count + 1 }
}
```

**Test Cases:**
- TC3.1.1: Child state var initialized correctly
- TC3.1.2: Child can read/write its state vars
- TC3.1.3: Forwarding to parent does not affect child state vars

---

### 3.2 State Variables in Parent Only (`52_hsm_state_vars_parent.fpy`)

**Objective:** Parent has state variables, accessed via forward.

```frame
$Child => $Parent {
    getCount(): int { => $^ }
}
$Parent {
    $.count: int = 100

    getCount(): int { return $.count }
}
```

**Test Cases:**
- TC3.2.1: Parent state var initialized when parent compartment created
- TC3.2.2: Parent handler can access `$.count` via its own compartment
- TC3.2.3: Child forwarding to parent allows parent to use its state vars

**NOTE:** This tests the bug documented in `40_hsm_parent_state_vars.fpy`

---

### 3.3 Same-Named Variables in Both - Independence (`53_hsm_state_vars_same_name.fpy`)

**Objective:** Child and parent can have state vars with the same name.

```frame
$Child => $Parent {
    $.value: int = 10

    getChildValue(): int { return $.value }
    getParentValue(): int { => $^ }
}
$Parent {
    $.value: int = 999

    getParentValue(): int { return $.value }
}
```

**Test Cases:**
- TC3.3.1: Child's `$.value` is 10
- TC3.3.2: Parent's `$.value` is 999
- TC3.3.3: No conflict or shadowing between compartments
- TC3.3.4: Each handler accesses its OWN `$.value`

---

### 3.4 Initialization with Literals (`54_hsm_state_vars_literals.fpy`)

**Objective:** State vars initialized with literal values.

```frame
$State {
    $.count: int = 0
    $.name: str = "default"
    $.items: list = []
    $.active: bool = True
}
```

**Test Cases:**
- TC3.4.1: Integer literal initialization
- TC3.4.2: String literal initialization
- TC3.4.3: List literal initialization
- TC3.4.4: Boolean literal initialization

---

### 3.5 Initialization with Expressions (`55_hsm_state_vars_expressions.fpy`)

**Objective:** State vars initialized with expressions.

```frame
$State {
    $.computed: int = 10 * 5 + 2
    $.concatenated: str = "hello" + "_world"
    $.called: int = get_initial_value()
}
```

**Test Cases:**
- TC3.5.1: Arithmetic expression evaluation
- TC3.5.2: String concatenation
- TC3.5.3: Function call during initialization

---

### 3.6 Initialization Referencing Domain Variables (`56_hsm_state_vars_from_domain.fpy`)

**Objective:** State vars initialized from domain variables.

```frame
@@system S {
    machine:
        $State {
            $.local: int = self.global_default
        }

    domain:
        global_default: int = 42
}
```

**Test Cases:**
- TC3.6.1: State var can reference domain var in initializer
- TC3.6.2: Domain var value at transition time is used
- TC3.6.3: Subsequent changes to domain var don't affect state var

---

### 3.7 Initialization Referencing State Parameters (`57_hsm_state_vars_from_params.fpy`)

**Objective:** State vars initialized from state parameters.

```frame
$State(multiplier: int) {
    $.value: int = 10 * self._compartment.state_args[0]
}
```

**Test Cases:**
- TC3.7.1: State param available during state var initialization
- TC3.7.2: Computed value based on state param is correct
- TC3.7.3: Re-entering state with different param reinitializes state vars

---

## 4. State Parameter Tests

### 4.1 Parameters on Child State (`58_hsm_child_params.fpy`)

**Objective:** Child state accepts parameters via transition.

```frame
$Start {
    go() { -> $Child(42) }
}
$Child(val: int) => $Parent {
    getVal(): int { return self._compartment.state_args[0] }
}
```

**Test Cases:**
- TC4.1.1: Child receives state parameter
- TC4.1.2: Parameter accessible within child handlers
- TC4.1.3: Forwarding to parent preserves child's params

---

### 4.2 Parameters on Parent State (`59_hsm_parent_params.fpy`)

**Objective:** Parent state has parameters (accessed when transitioning directly to parent).

```frame
$Child => $Parent {
    goToParent() { -> $Parent(100) }
}
$Parent(val: int) {
    getVal(): int { return self._compartment.state_args[0] }
}
```

**Test Cases:**
- TC4.2.1: Transitioning directly to parent passes params
- TC4.2.2: Parent params NOT set when child forwards to parent

---

### 4.3 Parameters at Both Levels (`60_hsm_params_both_levels.fpy`)

**Objective:** Both child and parent have state parameters.

```frame
$Child(c: int) => $Parent {
    // Child param accessible
}
$Parent(p: int) {
    // Parent param only when transitioned TO parent
}
```

**Test Cases:**
- TC4.3.1: Child params work independently
- TC4.3.2: Parent params only set on direct transition
- TC4.3.3: No cross-contamination between parameter spaces

---

### 4.4 Default Parameter Values (`61_hsm_params_defaults.fpy`)

**Objective:** State parameters with default values.

```frame
$State(val: int = 50) {
    getVal(): int { return self._compartment.state_args[0] if len(self._compartment.state_args) > 0 else 50 }
}
```

**Test Cases:**
- TC4.4.1: Default used when no param provided
- TC4.4.2: Explicit value overrides default
- TC4.4.3: Default works in HSM child states

---

### 4.5 Transition Chain with State Args (`62_hsm_transition_chain.fpy`)

**Objective:** Full transition syntax with exit, enter, and state args.

```frame
go() {
    ("exit_reason") -> ("enter_msg") $Target(state_val)
}
```

**Test Cases:**
- TC4.5.1: All three argument types passed correctly
- TC4.5.2: Exit handler receives exit args
- TC4.5.3: Enter handler receives enter args
- TC4.5.4: State params stored in compartment

---

## 5. Event Forwarding Tests

### 5.1 In-Handler Forward (`63_hsm_forward_in_handler.fpy`)

**Objective:** `=> $^` within a handler body.

```frame
$Child => $Parent {
    event() {
        log("Child processing")
        => $^
        log("After forward")  // This still executes
    }
}
```

**Test Cases:**
- TC5.1.1: Forward calls parent handler
- TC5.1.2: Code AFTER `=> $^` still executes
- TC5.1.3: Multiple forwards in same handler work

---

### 5.2 State-Level Default Forward (`64_hsm_forward_default.fpy`)

**Objective:** Bare `=> $^` as last entry in state.

```frame
$Child => $Parent {
    handled() { log("Child handles") }
    => $^  // All other events forward
}
```

**Test Cases:**
- TC5.2.1: Handled events NOT forwarded
- TC5.2.2: Unhandled events forwarded to parent
- TC5.2.3: `=> $^` must be last entry (syntax validation)

---

### 5.3 Multiple Forwards in Chain (`65_hsm_forward_chain.fpy`)

**Objective:** Forward through multiple hierarchy levels.

```frame
$Grandchild => $Child => $Parent
```

**Test Cases:**
- TC5.3.1: `=> $^` in grandchild forwards to child
- TC5.3.2: Child can then `=> $^` to parent
- TC5.3.3: Entire chain executes in order

---

### 5.4 Forward Then Transition (`66_hsm_forward_then_transition.fpy`)

**Objective:** Forward to parent, then transition.

```frame
$Child => $Parent {
    event() {
        => $^
        -> $OtherState
    }
}
```

**Test Cases:**
- TC5.4.1: Forward executes parent handler
- TC5.4.2: Transition still happens after forward
- TC5.4.3: Exit handler fires for child, not parent

---

### 5.5 Forward with Return Values (`67_hsm_forward_return.fpy`)

**Objective:** Forward when parent sets a return value.

```frame
$Child => $Parent {
    compute(): int {
        => $^  // Parent returns value
    }
}
$Parent {
    compute(): int {
        @@:return = 42
    }
}
```

**Test Cases:**
- TC5.5.1: Parent sets `@@:return`
- TC5.5.2: Child returns parent's value to caller
- TC5.5.3: Child can override return after forward

---

## 6. Variable Scope Tests

### 6.1 Domain Vars from Child and Parent (`68_hsm_scope_domain.fpy`)

**Objective:** Domain variables accessible from all levels.

```frame
$Child => $Parent {
    event() {
        self.domain_var = 10
        => $^
    }
}
$Parent {
    event() {
        self.domain_var = self.domain_var + 5
    }
}

domain:
    domain_var: int = 0
```

**Test Cases:**
- TC6.1.1: Child can access domain vars
- TC6.1.2: Parent can access same domain vars
- TC6.1.3: Changes by child visible to parent (same instance)

---

### 6.2 State Variables Isolated (`69_hsm_scope_state_vars.fpy`)

**Objective:** State vars scoped to their declaring state.

```frame
$Child => $Parent {
    $.child_val: int = 1
    // Cannot access $.parent_val
}
$Parent {
    $.parent_val: int = 2
    // Cannot access $.child_val
}
```

**Test Cases:**
- TC6.2.1: Child sees only `$.child_val`
- TC6.2.2: Parent sees only `$.parent_val`
- TC6.2.3: No cross-state variable access possible

---

### 6.3 Handler Parameters Scope (`70_hsm_scope_handler_params.fpy`)

**Objective:** Handler params scoped to handler.

```frame
$Child => $Parent {
    event(x: int) {
        // x available here
        => $^
        // x still available
    }
}
$Parent {
    event(x: int) {
        // This x is independent (from forwarded event)
    }
}
```

**Test Cases:**
- TC6.3.1: Child handler param `x` available in child
- TC6.3.2: Parent handler param `x` is same forwarded value
- TC6.3.3: Modifications to child's `x` don't affect parent's `x`

---

### 6.4 Enter/Exit Args Scope (`71_hsm_scope_enter_exit.fpy`)

**Objective:** Enter and exit args scoped appropriately.

```frame
$Child => $Parent {
    $>(msg: str) {
        // msg is enter arg
        log(msg)
    }
    <$(reason: str) {
        // reason is exit arg
        log(reason)
    }
}
```

**Test Cases:**
- TC6.4.1: Enter args bound to enter handler params
- TC6.4.2: Exit args bound to exit handler params
- TC6.4.3: Handler params independent of enter/exit args

---

### 6.5 Context (`@@`) Access from Child and Parent (`72_hsm_scope_context.fpy`)

**Objective:** `@@` refers to interface call context at all levels.

```frame
$Child => $Parent {
    compute(a: int): int {
        log(@@.a)  // Interface param
        => $^
    }
}
$Parent {
    compute(a: int): int {
        @@:return = @@.a * 2  // Same interface param
    }
}
```

**Test Cases:**
- TC6.5.1: Child handler can access `@@.a`
- TC6.5.2: Parent handler (via forward) sees same `@@.a`
- TC6.5.3: `@@:return` set by parent returned to original caller
- TC6.5.4: `@@:data` set by child visible to parent

---

## 7. Transition Tests

### 7.1 Parent to Child Transition (`73_hsm_transition_parent_to_child.fpy`)

**Objective:** Transition from parent state to child state.

```frame
$Parent {
    goToChild() { -> $Child }
}
$Child => $Parent {
    // Child is active, can forward to parent
}
```

**Test Cases:**
- TC7.1.1: Transition from parent to child works
- TC7.1.2: Child's enter handler fires
- TC7.1.3: Child can now forward to parent

---

### 7.2 Child to Sibling Transition (`74_hsm_transition_siblings.fpy`)

**Objective:** Transition between children of same parent.

```frame
$A => $Parent {
    goB() { -> $B }
}
$B => $Parent {
    goA() { -> $A }
}
```

**Test Cases:**
- TC7.2.1: A -> B transition works
- TC7.2.2: B -> A transition works
- TC7.2.3: Enter/exit handlers fire correctly
- TC7.2.4: Both siblings can still forward to parent

---

### 7.3 Transition with Full Args (`75_hsm_transition_full_args.fpy`)

**Objective:** Transitions with exit, enter, and state args.

```frame
$A => $Parent {
    goB() {
        ("exiting_A") -> ("entering_B") $B(42)
    }
}
$B(val: int) => $Parent {
    $>(msg: str) {
        log(f"Enter: {msg}, val: {val}")
    }
}
```

**Test Cases:**
- TC7.3.1: Exit args passed to A's exit handler
- TC7.3.2: Enter args passed to B's enter handler
- TC7.3.3: State args stored in B's compartment

---

### 7.4 Forward Transition (`-> =>`) (`76_hsm_forward_transition.fpy`)

**Objective:** Transition that also forwards the event.

```frame
$A {
    event() {
        -> => $B  // Transition and forward event
    }
}
$B {
    $>() { log("B entered") }
    event() { log("B handles event") }
}
```

**Test Cases:**
- TC7.4.1: Transition to B occurs
- TC7.4.2: B's enter handler fires
- TC7.4.3: Then B's event handler fires (forwarded event)

---

## 8. Stack Operations with HSM

### 8.1 Push Preserves Compartment Chain (`77_hsm_stack_push.fpy`)

**Objective:** Push from HSM child state preserves hierarchy.

```frame
$Child => $Parent {
    saveAndGo() {
        push$
        -> $Other
    }
}
$Other {
    restore() { -> pop$ }
}
```

**Test Cases:**
- TC8.1.1: Push saves child's compartment
- TC8.1.2: Transition to Other works
- TC8.1.3: Pop restores to Child state
- TC8.1.4: After pop, Child can still forward to Parent

---

### 8.2 Pop Restores Compartment Chain (`78_hsm_stack_pop.fpy`)

**Objective:** Pop restores full compartment including parent relationship.

**Test Cases:**
- TC8.2.1: State vars preserved through push/pop
- TC8.2.2: Parent relationship intact after pop
- TC8.2.3: Forwarding works after restoration

---

### 8.3 Stack with Sibling Push/Pop (`79_hsm_stack_siblings.fpy`)

**Objective:** Push from one sibling, pop from another.

```frame
$A => $Parent {
    save() { push$; -> $C }
}
$B => $Parent {
    // Can we pop to A?
}
$C {
    restoreToA() { -> pop$ }
}
```

**Test Cases:**
- TC8.3.1: Push A's compartment
- TC8.3.2: Go through various states
- TC8.3.3: Pop restores exactly to A
- TC8.3.4: A's state vars preserved

---

### 8.4 Stack with Deep Hierarchy (`80_hsm_stack_deep.fpy`)

**Objective:** Stack operations with multi-level hierarchy.

```frame
$Grandchild => $Child => $Parent {
    save() { push$; -> $Other }
}
```

**Test Cases:**
- TC8.4.1: Push from grandchild level
- TC8.4.2: Pop restores grandchild state
- TC8.4.3: Full hierarchy accessible after restore

---

## 9. Return Value Tests

### 9.1 Return from Child (`81_hsm_return_child.fpy`)

**Objective:** Child handler sets return value directly.

```frame
$Child => $Parent {
    compute(): int {
        @@:return = 42
    }
}
```

**Test Cases:**
- TC9.1.1: Child sets `@@:return`
- TC9.1.2: Value returned to caller
- TC9.1.3: No forward to parent needed

---

### 9.2 Return from Parent via Forward (`82_hsm_return_parent.fpy`)

**Objective:** Parent sets return value after forward.

```frame
$Child => $Parent {
    compute(): int {
        => $^
    }
}
$Parent {
    compute(): int {
        @@:return = 100
    }
}
```

**Test Cases:**
- TC9.2.1: Child forwards to parent
- TC9.2.2: Parent sets `@@:return = 100`
- TC9.2.3: Caller receives 100

---

### 9.3 Child Overrides Parent Return (`83_hsm_return_override.fpy`)

**Objective:** Child can override return value after forward.

```frame
$Child => $Parent {
    compute(): int {
        => $^
        @@:return = @@:return * 2  // Double parent's value
    }
}
$Parent {
    compute(): int {
        @@:return = 50
    }
}
```

**Test Cases:**
- TC9.3.1: Parent sets 50
- TC9.3.2: Child modifies to 100
- TC9.3.3: Caller receives 100

---

### 9.4 Return Value Initialization in HSM (`84_hsm_return_init.fpy`)

**Objective:** Return value initialization syntax in HSM context.

```frame
$Child => $Parent {
    compute(): int = default_value() {
        => $^
    }
}
```

**Test Cases:**
- TC9.4.1: Default initializer runs
- TC9.4.2: Parent can override
- TC9.4.3: Fallback to default if no override

---

## 10. Deep Hierarchy Tests

### 10.1 Three-Level Hierarchy Full Test (`85_hsm_three_level_full.fpy`)

**Objective:** Comprehensive test of 3-level hierarchy.

```frame
$Leaf => $Branch => $Root
```

**Test Cases:**
- TC10.1.1: Leaf handlers work
- TC10.1.2: Leaf forward to Branch
- TC10.1.3: Branch forward to Root
- TC10.1.4: Full chain forward (Leaf -> Branch -> Root)
- TC10.1.5: State vars at each level independent
- TC10.1.6: Domain vars shared across all levels
- TC10.1.7: Transitions between levels

---

### 10.2 Forward Through Multiple Levels (`86_hsm_forward_multi_level.fpy`)

**Objective:** Event forwarded through entire hierarchy.

```frame
$Leaf => $Branch => $Root {
    event() {
        log("Leaf")
        => $^
    }
}
$Branch => $Root {
    event() {
        log("Branch")
        => $^
    }
}
$Root {
    event() {
        log("Root")
        @@:return = "all_handled"
    }
}
```

**Test Cases:**
- TC10.2.1: All three handlers execute in order
- TC10.2.2: Log shows: Leaf, Branch, Root
- TC10.2.3: Return value set by Root returned to caller

---

### 10.3 Selective Forwarding (`87_hsm_selective_forward.fpy`)

**Objective:** Different events forwarded differently.

```frame
$Leaf => $Branch => $Root {
    event_a() {
        // Handle locally, no forward
    }
    event_b() {
        => $^  // Forward to Branch only
    }
    event_c() {
        // Handled in Branch, forwarded to Root
    }
    => $^  // Default forward
}
```

**Test Cases:**
- TC10.3.1: `event_a` handled by Leaf only
- TC10.3.2: `event_b` handled by Leaf then Branch
- TC10.3.3: Unknown events forward through entire chain

---

### 10.4 Mixed Hierarchy with Transitions (`88_hsm_mixed_transitions.fpy`)

**Objective:** Transitions within deep hierarchy.

```frame
$LeafA => $Branch
$LeafB => $Branch
$Branch => $Root
$Root

Transitions: LeafA -> LeafB -> Branch -> Root
```

**Test Cases:**
- TC10.4.1: Sibling leaf transitions
- TC10.4.2: Leaf to ancestor transitions
- TC10.4.3: Ancestor to leaf transitions
- TC10.4.4: Forward relationships maintained after transitions

---

## 11. Error Cases (Negative Tests)

### 11.1 Forward Without Parent (`89_hsm_error_no_parent.fpy`)

**Objective:** Verify error when `=> $^` used in state without parent.

```frame
$Orphan {
    event() {
        => $^  // ERROR: No parent
    }
}
```

**Expected:** Compilation error E4xx

---

### 11.2 Circular Hierarchy (`90_hsm_error_cycle.fpy`)

**Objective:** Verify error on circular parent relationships.

```frame
$A => $B
$B => $A  // ERROR: Cycle
```

**Expected:** Compilation error E4xx (HSM cycle detected)

---

### 11.3 Nonexistent Parent (`91_hsm_error_unknown_parent.fpy`)

**Objective:** Verify error when parent state doesn't exist.

```frame
$Child => $NonExistent  // ERROR: Unknown state
```

**Expected:** Compilation error E402

---

## Summary

| Category | Test Count | File Range |
|----------|------------|------------|
| HSM Structure | 4 | 41-44 |
| Enter/Exit Handlers | 6 | 45-50 |
| State Variables | 7 | 51-57 |
| State Parameters | 5 | 58-62 |
| Event Forwarding | 5 | 63-67 |
| Variable Scope | 5 | 68-72 |
| Transitions | 4 | 73-76 |
| Stack Operations | 4 | 77-80 |
| Return Values | 4 | 81-84 |
| Deep Hierarchy | 4 | 85-88 |
| Error Cases | 3 | 89-91 |

**Total: 51 new tests**

---

## Implementation Priority

### Phase 1: Core Functionality (Must Have)
- 1.1-1.4: HSM Structure
- 2.1-2.4: Enter/Exit Handlers
- 5.1-5.2: Event Forwarding (in-handler and default)

### Phase 2: State Management (Important)
- 3.1-3.3: State Variables
- 6.1-6.5: Variable Scope
- 9.1-9.2: Return Values

### Phase 3: Advanced Features (Nice to Have)
- 4.1-4.5: State Parameters
- 7.1-7.4: Transitions
- 8.1-8.4: Stack Operations
- 10.1-10.4: Deep Hierarchy

### Phase 4: Edge Cases and Validation
- 11.1-11.3: Error Cases
- 3.4-3.7: State Variable Initialization Edge Cases
- 9.3-9.4: Return Value Edge Cases

---

## Notes

1. **Compartment Architecture**: The current implementation may need work to support parent state variables (see `40_hsm_parent_state_vars.fpy` bug documentation).

2. **Forward Semantics**: V4 uses explicit-only forwarding. Events are NOT automatically forwarded to parents.

3. **State-Level Default Forward**: The `=> $^` at state level must be the LAST entry in the state block.

4. **Cross-Target Testing**: All tests should be created with `.fpy`, `.fts`, `.frs`, and `.fc` variants for multi-language validation.
