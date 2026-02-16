@@target python_3

@@system SystemReturnTest {
    interface:
        add(a: int, b: int): int
        multiply(a: int, b: int): int
        greet(name: str): str
        get_value(): int

    machine:
        $Calculator {
            $.value: int = 0

            add(a: int, b: int): int {
                ^ a + b
            }

            multiply(a: int, b: int): int {
                system.return = a * b
            }

            greet(name: str): str {
                ^ "Hello, " + name + "!"
            }

            get_value(): int {
                $.value = 42
                ^ $.value
            }
        }
}

def main():
    print("=== Test 13: System Return ===")
    calc = SystemReturnTest()

    # Test caret return sugar
    result = calc.add(3, 5)
    assert result == 8, f"Expected 8, got {result}"
    print(f"add(3, 5) = {result}")

    # Test system.return = expr
    result = calc.multiply(4, 7)
    assert result == 28, f"Expected 28, got {result}"
    print(f"multiply(4, 7) = {result}")

    # Test string return
    greeting = calc.greet("World")
    assert greeting == "Hello, World!", f"Expected 'Hello, World!', got '{greeting}'"
    print(f"greet('World') = {greeting}")

    # Test return with state variable
    value = calc.get_value()
    assert value == 42, f"Expected 42, got {value}"
    print(f"get_value() = {value}")

    print("PASS: System return works correctly")

if __name__ == '__main__':
    main()
