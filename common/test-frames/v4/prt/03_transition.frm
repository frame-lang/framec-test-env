@@target python_3

@@system WithTransition {
    interface:
        next()
        get_state(): str

    machine:
        $First {
            next() {
                print("Transitioning: First -> Second")
                -> $Second
            }

            get_state(): str {
                return "First"
            }
        }

        $Second {
            next() {
                print("Transitioning: Second -> First")
                -> $First
            }

            get_state(): str {
                return "Second"
            }
        }
}

def main():
    print("=== Test 03: State Transitions ===")
    s = WithTransition()

    # Initial state should be First
    state = s.get_state()
    assert state == "First", f"Expected 'First', got '{state}'"
    print(f"Initial state: {state}")

    # Transition to Second
    s.next()
    state = s.get_state()
    assert state == "Second", f"Expected 'Second', got '{state}'"
    print(f"After first next(): {state}")

    # Transition back to First
    s.next()
    state = s.get_state()
    assert state == "First", f"Expected 'First', got '{state}'"
    print(f"After second next(): {state}")

    print("PASS: State transitions work correctly")

if __name__ == '__main__':
    main()
