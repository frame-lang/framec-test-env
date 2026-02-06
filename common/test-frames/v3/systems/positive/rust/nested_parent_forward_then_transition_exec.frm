@@target rust

fn test_nested_parent_forward_then_transition() {
    // Test: transition
=> $^
                    }
-> $Next()
                }
            }
            $Next { }
            $Parent { }
    print("SUCCESS: test_nested_parent_forward_then_transition completed")
}

fn main() {
    test_nested_parent_forward_then_transition()
}
