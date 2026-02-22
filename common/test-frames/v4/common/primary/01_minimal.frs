@@target rust

@@system Minimal {
    interface:
        is_alive(): bool

    machine:
        $Start {
            is_alive(): bool {
                true
            }
        }
}

fn main() {
    println!("=== Test 01: Minimal System ===");
    let mut s = Minimal::new();

    // Test that system instantiates and responds
    let result = s.is_alive();
    assert_eq!(result, true, "Expected true, got {}", result);
    println!("is_alive() = {}", result);

    println!("PASS: Minimal system works correctly");
}
