@@target c

fn test_block_scope() {
    // Test: transition
    int x = 2; => $^; }
                    x = 3;
                }
            }
            $P { }
    print("SUCCESS: test_block_scope completed")
}

fn main() {
    test_block_scope()
}
