@@target python

fn test_multi_items_map() {
    // Test: transition
    # native pre
=> $^
        # between
-> $Next(42, "ok")
        # native post
    print("SUCCESS: test_multi_items_map completed")
}

fn main() {
    test_multi_items_map()
}
