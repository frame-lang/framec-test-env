@@target rust

// Tests basic system.return functionality in Rust
// Note: Rust uses native return, not _return_value pattern

@@system SystemReturnDefaultTest {
    interface:
        handler_sets_value(): i32
        handler_returns_computed(): i32
        get_count(): i32

    machine:
        $Start {
            $.count: i32 = 0

            handler_sets_value(): i32 {
                return 42;
            }

            handler_returns_computed(): i32 {
                $.count = $.count + 1;
                return $.count;
            }

            get_count(): i32 {
                return $.count;
            }
        }
}

fn main() {
    println!("=== Test 14: System Return Behavior (Rust) ===");
    let mut s = SystemReturnDefaultTest::new();

    // Test 1: Handler explicitly sets return value
    let result = s.handler_sets_value();
    assert_eq!(result, 42, "Expected 42, got {}", result);
    println!("1. handler_sets_value() = {}", result);

    // Test 2: Handler computes and returns value
    let result = s.handler_returns_computed();
    assert_eq!(result, 1, "Expected 1, got {}", result);
    println!("2. handler_returns_computed() = {}", result);

    // Test 3: Verify side effect
    let count = s.get_count();
    assert_eq!(count, 1, "Expected count=1, got {}", count);
    println!("3. get_count() = {}", count);

    // Test 4: Call again
    let result = s.handler_returns_computed();
    assert_eq!(result, 2, "Expected 2, got {}", result);
    println!("4. handler_returns_computed() again = {}", result);

    println!("PASS: System return behavior works correctly");
}
