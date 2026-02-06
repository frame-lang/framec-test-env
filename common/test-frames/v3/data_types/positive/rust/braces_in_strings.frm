@@target rust

fn test_braces_in_strings() {
    // Test: string handling
    let s = "brace } inside string";
        // comment with }
        let t = format!("brace {{}} {}", 1 + 2);
    print("SUCCESS: test_braces_in_strings completed")
}

fn main() {
    test_braces_in_strings()
}
