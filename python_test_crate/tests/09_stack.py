from typing import Any, Optional, List, Dict, Callable

class StackOps:
    def __init__(self):
        self._state_stack = []
        self._state_context = {}
        self._return_value = None
        self._state = "Main"
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
        # No enter handlers
        pass

    def _exit(self, *args):
        # No exit handlers
        pass

    def push_and_go(self):
        self._dispatch_event("push_and_go")

    def pop_back(self):
        self._dispatch_event("pop_back")

    def do_work(self) -> str:
        self._return_value = None
        self._dispatch_event("do_work")
        return self._return_value

    def get_state(self) -> str:
        self._return_value = None
        self._dispatch_event("get_state")
        return self._return_value

    def _s_Sub_pop_back(self):
        print("Popping back to previous state")
        __saved = self._state_stack.pop()
        self._exit()
        self._state = __saved[0]
        self._state_context = __saved[1]
        return

    def _s_Sub_push_and_go(self):
        print("Already in Sub")

    def _s_Sub_do_work(self) -> str:
        self._return_value = "Working in Sub"
        return

    def _s_Sub_get_state(self) -> str:
        self._return_value = "Sub"
        return

    def _s_Main_push_and_go(self):
        print("Pushing Main to stack, going to Sub")
        self._state_stack.append((self._state, self._state_context.copy()))
        self._transition("Sub", None, None)

    def _s_Main_do_work(self) -> str:
        self._return_value = "Working in Main"
        return

    def _s_Main_pop_back(self):
        print("Cannot pop - nothing on stack in Main")

    def _s_Main_get_state(self) -> str:
        self._return_value = "Main"
        return


def main():
    print("=== Test 09: Stack Push/Pop ===")
    s = StackOps()

    # Initial state should be Main
    state = s.get_state()
    assert state == "Main", f"Expected 'Main', got '{state}'"
    print(f"Initial state: {state}")

    # Do work in Main
    work = s.do_work()
    assert work == "Working in Main", f"Expected 'Working in Main', got '{work}'"
    print(f"do_work(): {work}")

    # Push and go to Sub
    s.push_and_go()
    state = s.get_state()
    assert state == "Sub", f"Expected 'Sub', got '{state}'"
    print(f"After push_and_go(): {state}")

    # Do work in Sub
    work = s.do_work()
    assert work == "Working in Sub", f"Expected 'Working in Sub', got '{work}'"
    print(f"do_work(): {work}")

    # Pop back to Main
    s.pop_back()
    state = s.get_state()
    assert state == "Main", f"Expected 'Main' after pop, got '{state}'"
    print(f"After pop_back(): {state}")

    print("PASS: Stack push/pop works correctly")

if __name__ == '__main__':
    main()

