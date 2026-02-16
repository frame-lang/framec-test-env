@@target typescript

// Tests that system.return follows "last writer wins" across transition lifecycle

@@system SystemReturnChainTest {
    interface:
        test_enter_sets(): string
        test_exit_then_enter(): string
        get_state(): string

    machine:
        $Start {
            test_enter_sets(): string {
                -> $EnterSetter
            }

            test_exit_then_enter(): string {
                -> $BothSet
            }

            get_state(): string {
                return "Start"
            }

            $<() {
                // Exit handler sets initial value
                system.return = "from_exit"
            }
        }

        $EnterSetter {
            $>() {
                // Enter handler sets return value
                system.return = "from_enter"
            }

            get_state(): string {
                return "EnterSetter"
            }
        }

        $BothSet {
            $>() {
                // Enter handler sets return - should overwrite exit's value
                system.return = "enter_wins"
            }

            get_state(): string {
                return "BothSet"
            }
        }
}

function main(): void {
    console.log("=== Test 15: System Return Chain (Last Writer Wins) (TypeScript) ===");

    // Test 1: Start exit + EnterSetter enter
    // Start's exit sets "from_exit", EnterSetter's enter sets "from_enter"
    // Enter should win (last writer)
    const s1 = new SystemReturnChainTest();
    let result = s1.test_enter_sets();
    if (result !== "from_enter") {
        throw new Error(`Expected 'from_enter', got '${result}'`);
    }
    if (s1.get_state() !== "EnterSetter") {
        throw new Error(`Expected state 'EnterSetter'`);
    }
    console.log(`1. Exit set then enter set - enter wins: '${result}'`);

    // Test 2: Both handlers set, enter wins
    const s2 = new SystemReturnChainTest();
    result = s2.test_exit_then_enter();
    if (result !== "enter_wins") {
        throw new Error(`Expected 'enter_wins', got '${result}'`);
    }
    if (s2.get_state() !== "BothSet") {
        throw new Error(`Expected state 'BothSet'`);
    }
    console.log(`2. Both set - enter wins: '${result}'`);

    console.log("PASS: System return chain (last writer wins) works correctly");
}

main();
