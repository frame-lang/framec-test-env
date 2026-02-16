@@target typescript

@@system StateVarReentry {
    interface:
        increment(): int
        get_count(): int
        go_other()
        come_back()

    machine:
        $Counter {
            $.count: int = 0

            increment(): int {
                $.count = $.count + 1
                return $.count
            }

            get_count(): int {
                return $.count
            }

            go_other() {
                -> $Other
            }
        }

        $Other {
            come_back() {
                -> $Counter
            }

            increment(): int {
                return -1
            }

            get_count(): int {
                return -1
            }
        }
}

function main() {
    console.log("=== Test 11: State Variable Reentry (TypeScript) ===");
    const s = new StateVarReentry();

    // Increment a few times
    s.increment();
    s.increment();
    let count = s.get_count();
    if (count !== 2) throw new Error(`Expected 2 after two increments, got ${count}`);
    console.log(`Count before leaving: ${count}`);

    // Leave the state
    s.go_other();
    console.log("Transitioned to Other state");

    // Come back - state var should be reinitialized to 0
    s.come_back();
    count = s.get_count();
    if (count !== 0) throw new Error(`Expected 0 after re-entering Counter (state var reinit), got ${count}`);
    console.log(`Count after re-entering Counter: ${count}`);

    // Increment again to verify it works
    const result = s.increment();
    if (result !== 1) throw new Error(`Expected 1 after increment, got ${result}`);
    console.log(`After increment: ${result}`);

    console.log("PASS: State variables reinitialize on state reentry");
}

main();
