@@target rust

fn test_unterminated_raw_string() {
    // Test: string handling
    let a = r#"unterminated raw string...
    print("SUCCESS: test_unterminated_raw_string completed")
}

fn main() {
    test_unterminated_raw_string()
}
