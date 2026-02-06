@@target typescript

fn test_else_if_chain() {
    // Test: transition
    if (x) {
            // body
-> $B()
        }
        else if (y) {
            // body
        }
    print("SUCCESS: test_else_if_chain completed")
}

fn main() {
    test_else_if_chain()
}
