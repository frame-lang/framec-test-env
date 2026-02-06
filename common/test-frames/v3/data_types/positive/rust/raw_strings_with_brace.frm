@@target rust

fn test_raw_strings_with_brace() {
    // Test: string handling
    let a = r#"brace } in raw"#;
        let b = r###"raw with } and nested ### delims"###;
        let c = "normal }";
    print("SUCCESS: test_raw_strings_with_brace completed")
}

fn main() {
    test_raw_strings_with_brace()
}
