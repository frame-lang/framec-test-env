@@target cpp

fn test_try_catch() {
    // Test: transition
    try {
            // body
-> $Next()
        }
        catch (const std::exception& ex) {
            // handler
        }
    print("SUCCESS: test_try_catch completed")
}

fn main() {
    test_try_catch()
}
