@@target python

fn test_braces_in_strings() {
    // Test: string handling
    s = "brace } inside string"
    # comment with }
    f = f"value={{1+2}}"
    print("SUCCESS: test_braces_in_strings completed")
}

fn main() {
    test_braces_in_strings()
}
