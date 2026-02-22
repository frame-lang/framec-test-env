@@target python_3

@@system Minimal {
    interface:
        is_alive(): bool

    machine:
        $Start {
            is_alive(): bool {
                return True
            }
        }
}

def main():
    print("=== Test 01: Minimal System ===")
    s = Minimal()

    # Test that system instantiates and responds
    result = s.is_alive()
    assert result == True, f"Expected True, got {result}"
    print(f"is_alive() = {result}")

    print("PASS: Minimal system works correctly")

if __name__ == '__main__':
    main()
