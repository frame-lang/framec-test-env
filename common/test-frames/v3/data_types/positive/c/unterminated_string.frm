@@target c

fn test_unterminated_string() {
    // Test: string handling
    const char* s = "no close;
    print("SUCCESS: test_unterminated_string completed")
}

fn main() {
    test_unterminated_string()
}
