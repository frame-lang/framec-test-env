@@target python_3

@@system PushNamedStateTest {
    interface:
        pushB()
        goToB()
        pop()
        getState(): str

    machine:
        $A {
            pushB() {
                print("Pushing B onto stack from A")
                `push$ $B
            }

            goToB() {
                print("Transitioning to B")
                -> $B
            }

            pop() {
                print("Pop in A - nothing to pop, staying in A")
            }

            getState(): str {
                return "A"
            }
        }

        $B {
            pushB() {
                print("Already in B")
            }

            goToB() {
                print("Already in B")
            }

            pop() {
                print("Popping from B back to previous state")
                `-> pop$
            }

            getState(): str {
                return "B"
            }
        }
}

def main():
    print("=== Test 21: Push Named State ===")
    s = PushNamedStateTest()

    # Initial state should be A
    state = s.getState()
    print(f"1. Initial state: {state}")
    assert state == "A", f"Expected 'A', got '{state}'"

    # Push B onto the stack (doesn't change state)
    s.pushB()
    state = s.getState()
    print(f"2. After pushB() - still in: {state}")
    assert state == "A", f"Expected 'A' after push (no transition), got '{state}'"

    # Transition to B
    s.goToB()
    state = s.getState()
    print(f"3. After goToB() - now in: {state}")
    assert state == "B", f"Expected 'B' after transition, got '{state}'"

    # Pop should restore to B (what we pushed), not A
    s.pop()
    state = s.getState()
    print(f"4. After pop() - restored to: {state}")
    assert state == "B", f"Expected 'B' after pop (pushed state), got '{state}'"

    print("PASS: Push named state with full workflow works correctly")

if __name__ == '__main__':
    main()
