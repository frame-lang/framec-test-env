from typing import Any, Optional, List, Dict, Callable

class SystemReturnTest:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self._state = "Calculator"
        self._enter()

    def _transition(self, target_state, exit_args = None, enter_args = None):
        if exit_args:
            self._exit(*exit_args)
        else:
            self._exit()
        self._state = target_state
        if enter_args:
            self._enter(*enter_args)
        else:
            self._enter()

    def _change_state(self, target_state):
        self._state = target_state

    def _dispatch_event(self, event, *args):
        handler_name = f"_s_{self._state}_{event}"
        handler = getattr(self, handler_name, None)
        if handler:
            return handler(*args)

    def _enter(self, *args):
        if self._state == "Calculator":
            self._state_context["value"] = 0


    def _exit(self, *args):
        # No exit handlers
        pass

    def add(self, a: int, b: int) -> int:
        self._return_value = None
        self._dispatch_event("add", a, b)
        return self._return_value

    def multiply(self, a: int, b: int) -> int:
        self._return_value = None
        self._dispatch_event("multiply", a, b)
        return self._return_value

    def greet(self, name: str) -> str:
        self._return_value = None
        self._dispatch_event("greet", name)
        return self._return_value

    def get_value(self) -> int:
        self._return_value = None
        self._dispatch_event("get_value")
        return self._return_value

    def _s_Calculator_greet(self, name: str) -> str:
        self._return_value = "Hello, " + name + "!"
        return

    def _s_Calculator_multiply(self, a: int, b: int) -> int:
        self._return_value = a * b

    def _s_Calculator_get_value(self) -> int:
        self._state_context["value"] = 42
        self._return_value = self._state_context["value"]
        return

    def _s_Calculator_add(self, a: int, b: int) -> int:
        self._return_value = a + b
        return


def main():
    print("=== Test 13: System Return ===")
    calc = SystemReturnTest()

    # Test return sugar
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

