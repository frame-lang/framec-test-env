@@target typescript

@@system SystemReturnChainTest {
    interface:
        test_exit_sets(): string = "default"
        test_enter_sets(): string = "default"
        test_both_set(): string = "default"
        get_state(): string

    machine:
        $Start {
            test_exit_sets(): string {
                ("exit_value") -> $StateB
            }

            test_enter_sets(): string {
                -> ("enter_arg") $StateC
            }

            test_both_set(): string {
                ("exit_val") -> ("enter_val") $StateD
            }

            get_state(): string {
                ^ "Start"
            }

            $<(msg: string) {
                system.return = msg
            }
        }

        $StateB {
            get_state(): string {
                ^ "StateB"
            }
        }

        $StateC {
            $>(arg: string) {
                system.return = arg
            }

            get_state(): string {
                ^ "StateC"
            }
        }

        $StateD {
            $>(arg: string) {
                system.return = "enter_wins"
            }

            get_state(): string {
                ^ "StateD"
            }
        }
}

function main(): void {
    console.log("=== Test 15: System Return Chain (TypeScript) ===");

    // Test 1: Exit handler sets return
    const s1 = new SystemReturnChainTest();
    let result = s1.test_exit_sets();
    if (result !== "exit_value") {
        throw new Error(`Expected 'exit_value', got '${result}'`);
    }
    if (s1.get_state() !== "StateB") {
        throw new Error(`Expected state 'StateB'`);
    }
    console.log(`1. Exit handler set return: '${result}'`);

    // Test 2: Enter handler sets return
    const s2 = new SystemReturnChainTest();
    result = s2.test_enter_sets();
    if (result !== "enter_arg") {
        throw new Error(`Expected 'enter_arg', got '${result}'`);
    }
    console.log(`2. Enter handler set return: '${result}'`);

    // Test 3: Both set - enter wins
    const s3 = new SystemReturnChainTest();
    result = s3.test_both_set();
    if (result !== "enter_wins") {
        throw new Error(`Expected 'enter_wins', got '${result}'`);
    }
    console.log(`3. Both handlers set - enter wins: '${result}'`);

    console.log("PASS: System return chain works correctly");
}

main();
