@@target typescript

fn test_else_if_else_chain() {
    // Test: transition
    if (x) {
            // body
-> $B()
        }
        else if (y) {
            // body
        }
        else {
            // tail
        }
    print("SUCCESS: test_else_if_else_chain completed")
}

fn main() {
    test_else_if_else_chain()
}
