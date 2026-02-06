@@target cpp

fn test_strings_and_comments_with_brace() {
    // Test: string handling
    // comment with }
        const char* s = "brace } inside string";
        /* block with } */
    print("SUCCESS: test_strings_and_comments_with_brace completed")
}

fn main() {
    test_strings_and_comments_with_brace()
}
