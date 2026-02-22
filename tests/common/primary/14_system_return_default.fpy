@@target python_3

# NOTE: Default return value syntax (method(): type = default) not yet implemented.
# This test validates behavior when handler doesn't set system.return.

@@system SystemReturnDefaultTest {
    interface:
        handler_sets_value(): str
        handler_no_return(): str
        get_count(): int

    machine:
        $Start {
            $.count: int = 0

            handler_sets_value(): str {
                return "set_by_handler"
            }

            handler_no_return(): str {
                # Does not set return - should return None
                $.count = $.count + 1
            }

            get_count(): int {
                return $.count
            }
        }
}

def main():
    print("=== Test 14: System Return Default Behavior ===")
    s = SystemReturnDefaultTest()

    # Test 1: Handler explicitly sets return value
    result = s.handler_sets_value()
    assert result == "set_by_handler", f"Expected 'set_by_handler', got '{result}'"
    print(f"1. handler_sets_value() = '{result}'")

    # Test 2: Handler does NOT set return - should return None
    result = s.handler_no_return()
    assert result is None, f"Expected None, got '{result}'"
    print(f"2. handler_no_return() = {result}")

    # Test 3: Verify handler was called (side effect check)
    count = s.get_count()
    assert count == 1, f"Expected count=1, got {count}"
    print(f"3. Handler was called, count = {count}")

    # Test 4: Call again to verify idempotence
    result = s.handler_no_return()
    assert result is None, f"Expected None again, got '{result}'"
    count = s.get_count()
    assert count == 2, f"Expected count=2, got {count}"
    print(f"4. Second call: result={result}, count={count}")

    print("PASS: System return default behavior works correctly")

if __name__ == '__main__':
    main()
