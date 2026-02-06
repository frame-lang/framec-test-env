@@target rust

fn test_nested_block_transition_then_native_ok() {
    // Test: transition
-> $B() }
                    let n = 1; // allowed: transition was last in its inner block
                }
            }
            $B { e() { } }
    print("SUCCESS: test_nested_block_transition_then_native_ok completed")
}

fn main() {
    test_nested_block_transition_then_native_ok()
}
