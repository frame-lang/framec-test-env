@@target csharp

fn test_verbatim_and_raw() {
    // Test: string handling
    var a = @"brace } in verbatim";
        var b = $@"interp {1 + 2} with }} brace";
        var c = """raw quote with }""";
    print("SUCCESS: test_verbatim_and_raw completed")
}

fn main() {
    test_verbatim_and_raw()
}
