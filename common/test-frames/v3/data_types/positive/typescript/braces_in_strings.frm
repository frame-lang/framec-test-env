@@target typescript

fn test_braces_in_strings() {
    // Test: string handling
    const s = "brace } inside string";
        // comment with }
        const t = `template with } and ${1 + 2}`;
    print("SUCCESS: test_braces_in_strings completed")
}

fn main() {
    test_braces_in_strings()
}
