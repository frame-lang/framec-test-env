@@target rust

@@system SystemReturnChainTest {
    interface:
        test_exit_sets(): i32 = 0
        test_enter_sets(): i32 = 0
        test_both_set(): i32 = 0
        get_state_num(): i32

    machine:
        $Start {
            test_exit_sets(): i32 {
                (100) -> $StateB
            }

            test_enter_sets(): i32 {
                -> (200) $StateC
            }

            test_both_set(): i32 {
                (300) -> (400) $StateD
            }

            get_state_num(): i32 {
                ^ 1
            }

            $<(val: i32) {
                system.return = val
            }
        }

        $StateB {
            get_state_num(): i32 {
                ^ 2
            }
        }

        $StateC {
            $>(val: i32) {
                system.return = val
            }

            get_state_num(): i32 {
                ^ 3
            }
        }

        $StateD {
            $>(val: i32) {
                // Enter wins - ignore val, set our own
                system.return = 999
            }

            get_state_num(): i32 {
                ^ 4
            }
        }
}

fn main() {
    println!("=== Test 15: System Return Chain (Rust) ===");

    // Test 1: Exit handler sets return
    let mut s1 = SystemReturnChainTest::new();
    let result = s1.test_exit_sets();
    assert_eq!(result, 100, "Expected 100, got {}", result);
    assert_eq!(s1.get_state_num(), 2, "Expected state 2");
    println!("1. Exit handler set return: {}", result);

    // Test 2: Enter handler sets return
    let mut s2 = SystemReturnChainTest::new();
    let result = s2.test_enter_sets();
    assert_eq!(result, 200, "Expected 200, got {}", result);
    assert_eq!(s2.get_state_num(), 3, "Expected state 3");
    println!("2. Enter handler set return: {}", result);

    // Test 3: Both set - enter wins (last writer)
    let mut s3 = SystemReturnChainTest::new();
    let result = s3.test_both_set();
    assert_eq!(result, 999, "Expected 999 (enter wins), got {}", result);
    assert_eq!(s3.get_state_num(), 4, "Expected state 4");
    println!("3. Both handlers set - enter wins: {}", result);

    println!("PASS: System return chain works correctly");
}
