@@target typescript

fn test_try_catch_finally() {
    // Test: transition
    try {
            // body
-> $B()
        } catch (e) {
            // handler
        } finally {
            // cleanup
        }
    print("SUCCESS: test_try_catch_finally completed")
}

fn main() {
    test_try_catch_finally()
}
