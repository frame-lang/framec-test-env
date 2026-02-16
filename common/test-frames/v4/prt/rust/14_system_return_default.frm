@@target rust

@@system SystemReturnDefaultTest {
    interface:
        get_count(): i32 = -1
        get_code(): i32 = 999
        handler_sets_value(): i32 = 0

    machine:
        $Start {
            get_count(): i32 {
                // No return - should use default -1
            }

            get_code(): i32 {
                // No return - should use default 999
            }

            handler_sets_value(): i32 {
                ^ 42
            }
        }
}

fn main() {
    println!("=== Test 14: System Return Default Values (Rust) ===");
    let mut s = SystemReturnDefaultTest::new();

    // Test 1: Default when handler doesn't set
    let result = s.get_count();
    assert_eq!(result, -1, "Expected -1, got {}", result);
    println!("1. get_count() (no handler set) = {}", result);

    // Test 2: Another default value
    let result = s.get_code();
    assert_eq!(result, 999, "Expected 999, got {}", result);
    println!("2. get_code() (no handler set) = {}", result);

    // Test 3: Handler sets value - should override default
    let result = s.handler_sets_value();
    assert_eq!(result, 42, "Expected 42, got {}", result);
    println!("3. handler_sets_value() = {}", result);

    println!("PASS: System return default values work correctly");
}
