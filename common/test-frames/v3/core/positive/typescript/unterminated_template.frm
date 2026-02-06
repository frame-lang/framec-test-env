@@target typescript

fn test_unterminated_template() {
    // Test: feature
    const t = `unterminated ${1 + 2}
    print("SUCCESS: test_unterminated_template completed")
}

fn main() {
    test_unterminated_template()
}
