@@target python

fn test_elif_chain() {
    // Test: transition
    if x:
            pass
-> $B()
        elif y:
            pass
    print("SUCCESS: test_elif_chain completed")
}

fn main() {
    test_elif_chain()
}
