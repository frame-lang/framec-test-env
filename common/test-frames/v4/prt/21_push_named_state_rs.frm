@@target rust

@@system PushNamedStateTest {
    interface:
        push_b()
        go_to_b()
        pop()
        get_state(): String

    machine:
        $A {
            push_b() {
                println!("Pushing B onto stack from A");
                `push$ $B
            }

            go_to_b() {
                println!("Transitioning to B");
                -> $B
            }

            pop() {
                println!("Pop in A - nothing to pop, staying in A");
            }

            get_state(): String {
                return "A".to_string();
            }
        }

        $B {
            push_b() {
                println!("Already in B");
            }

            go_to_b() {
                println!("Already in B");
            }

            pop() {
                println!("Popping from B back to previous state");
                `-> pop$
            }

            get_state(): String {
                return "B".to_string();
            }
        }
}

fn main() {
    println!("=== Test 21: Push Named State (Rust) ===");
    let mut s = PushNamedStateTest::new();

    // Initial state should be A
    let state = s.get_state();
    println!("1. Initial state: {}", state);
    assert_eq!(state, "A", "Expected 'A', got '{}'", state);

    // Push B onto the stack (doesn't change state)
    s.push_b();
    let state = s.get_state();
    println!("2. After push_b() - still in: {}", state);
    assert_eq!(state, "A", "Expected 'A' after push (no transition), got '{}'", state);

    // Transition to B
    s.go_to_b();
    let state = s.get_state();
    println!("3. After go_to_b() - now in: {}", state);
    assert_eq!(state, "B", "Expected 'B' after transition, got '{}'", state);

    // Pop should restore to B (what we pushed), not A
    s.pop();
    let state = s.get_state();
    println!("4. After pop() - restored to: {}", state);
    assert_eq!(state, "B", "Expected 'B' after pop (pushed state), got '{}'", state);

    println!("PASS: Push named state with full workflow works correctly");
}
