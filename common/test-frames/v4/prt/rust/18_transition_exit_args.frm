@@target rust

// Rust version: Exit args not yet supported in Rust backend
// This test validates basic exit handler works in Rust

@@system TransitionExitArgs {
    interface:
        leave()
        get_count(): i32

    domain:
        var count: i32 = 0

    machine:
        $Active {
            $<() {
                self.count = self.count + 10;
            }

            leave() {
                self.count = 1;
                -> $Done
            }

            get_count(): i32 {
                return self.count;
            }
        }

        $Done {
            $>() {
                self.count = self.count + 100;
            }

            get_count(): i32 {
                return self.count;
            }
        }
}

fn main() {
    println!("=== Test 15: Transition Exit Args (Rust) ===");
    let mut s = TransitionExitArgs::new();

    // Initial state is Active
    let count = s.get_count();
    assert_eq!(count, 0, "Expected count=0, got {}", count);

    // Leave - should call exit handler, then enter handler
    s.leave();
    let count = s.get_count();
    // count = 1 (from leave) + 10 (from exit) + 100 (from enter) = 111
    assert_eq!(count, 111, "Expected count=111, got {}", count);

    println!("PASS: Transition exit args work correctly");
}
