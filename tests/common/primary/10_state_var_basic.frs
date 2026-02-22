@@target rust

@@system StateVarBasic {
    interface:
        increment(): i32
        get_count(): i32
        reset()

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

            reset() {
                $.count = 0;
            }
        }
}

fn main() {
    println!("=== Test 10: State Variable Basic ===");
    let mut s = StateVarBasic::new();

    // Initial value should be 0
    let count = s.get_count();
    assert_eq!(count, 0, "Expected 0, got {}", count);
    println!("Initial count: {}", count);

    // Increment should return new value
    let result = s.increment();
    assert_eq!(result, 1, "Expected 1 after first increment, got {}", result);
    println!("After first increment: {}", result);

    // Second increment
    let result = s.increment();
    assert_eq!(result, 2, "Expected 2 after second increment, got {}", result);
    println!("After second increment: {}", result);

    // Reset should set back to 0
    s.reset();
    let count = s.get_count();
    assert_eq!(count, 0, "Expected 0 after reset, got {}", count);
    println!("After reset: {}", count);

    println!("PASS: State variable basic operations work correctly");
}
