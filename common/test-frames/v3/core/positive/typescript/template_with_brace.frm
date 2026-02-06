@@target typescript

fn test_template_with_brace() {
    // Test: comment parsing
    const s = `brace } and nested ${`x${1}`}`;
        /* } in comment */
    print("SUCCESS: test_template_with_brace completed")
}

fn main() {
    test_template_with_brace()
}
