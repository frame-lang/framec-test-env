@@target rust

fn test_try_forward_and_stack_finally_transition() {
    // Test: transition
=> $^
$$[+]
                    }
$$[-]
-> $B()
                }
            }
            $B { e() { } }
    print("SUCCESS: test_try_forward_and_stack_finally_transition completed")
}

fn main() {
    test_try_forward_and_stack_finally_transition()
}
