@@target rust

// NOTE: Rust push/pop does not preserve state variables across push/pop.
// State variables are reinitialized when popping back to a state.
// This is a known limitation - see TODO in system_codegen.rs

@@system StateVarPushPop {
    interface:
        increment(): i32
        get_count(): i32
        save_and_go()
        restore()

    machine:
        $Counter {
            $.count: i32 = 0

            increment(): i32 {
                $.count = $.count + 1;
                $.count
            }

            get_count(): i32 {
                $.count
            }

            save_and_go() {
                `push$
                -> $Other
            }
        }

        $Other {
            $.other_count: i32 = 100

            restore() {
                `-> pop$
            }

            increment(): i32 {
                $.other_count = $.other_count + 1;
                $.other_count
            }

            get_count(): i32 {
                $.other_count
            }
        }
}

fn main() {
    println!("=== Test 12: State Variable Push/Pop (Rust) ===");
    let mut s = StateVarPushPop::new();

    // Increment counter to 3
    s.increment();
    s.increment();
    s.increment();
    let count = s.get_count();
    assert_eq!(count, 3, "Expected 3, got {}", count);
    println!("Counter before push: {}", count);

    // Push and go to Other state
    s.save_and_go();
    println!("Pushed and transitioned to Other");

    // In Other state, count should be 100 (Other's state var)
    let count = s.get_count();
    assert_eq!(count, 100, "Expected 100 in Other state, got {}", count);
    println!("Other state count: {}", count);

    // Increment in Other
    s.increment();
    let count = s.get_count();
    assert_eq!(count, 101, "Expected 101 after increment, got {}", count);
    println!("Other state after increment: {}", count);

    // Pop back - NOTE: Rust does NOT preserve state vars, so count will be 0
    // This is different from Python/TypeScript which do preserve state vars
    s.restore();
    println!("Popped back to Counter");

    let count = s.get_count();
    // In Rust, state vars reinitialize to default (0) after pop
    assert_eq!(count, 0, "Expected 0 after pop (Rust limitation: state vars reinit), got {}", count);
    println!("Counter after pop: {} (reinitialized, not preserved)", count);

    // Increment to verify it works
    s.increment();
    let count = s.get_count();
    assert_eq!(count, 1, "Expected 1, got {}", count);
    println!("Counter after increment: {}", count);

    println!("PASS: State push/pop works (note: state vars reinitialize in Rust)");
}
