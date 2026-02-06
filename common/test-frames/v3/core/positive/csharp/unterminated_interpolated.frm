@@target csharp

fn test_unterminated_interpolated() {
    // Test: string handling
    var s = @"unterminated verbatim string...
    print("SUCCESS: test_unterminated_interpolated completed")
}

fn main() {
    test_unterminated_interpolated()
}
