@@target rust

fn test_nested_loops_inline_stack_then_transition() {
    // Test: transition
    // nested block as a stand-in for loops
$$[+]
                        { $$[-] }
                    }
-> $B()
                }
            }
            $B { e() { } }
    print("SUCCESS: test_nested_loops_inline_stack_then_transition completed")
}

fn main() {
    test_nested_loops_inline_stack_then_transition()
}
