@@target typescript

// Tests system.return behavior - TypeScript version focuses on explicit returns
// (TypeScript's type system requires functions with return types to return values)

@@system SystemReturnDefaultTest {
    interface:
        handler_sets_value(): string
        handler_returns_computed(): string
        get_count(): number

    machine:
        $Start {
            $.count: number = 0

            handler_sets_value(): string {
                return "set_by_handler"
            }

            handler_returns_computed(): string {
                $.count = $.count + 1
                return "computed_" + String($.count)
            }

            get_count(): number {
                return $.count
            }
        }
}

function main(): void {
    console.log("=== Test 14: System Return Behavior (TypeScript) ===");
    const s = new SystemReturnDefaultTest();

    // Test 1: Handler explicitly sets return value
    let result: string = s.handler_sets_value();
    if (result !== "set_by_handler") {
        throw new Error(`Expected 'set_by_handler', got '${result}'`);
    }
    console.log(`1. handler_sets_value() = '${result}'`);

    // Test 2: Handler computes and returns value
    result = s.handler_returns_computed();
    if (result !== "computed_1") {
        throw new Error(`Expected 'computed_1', got '${result}'`);
    }
    console.log(`2. handler_returns_computed() = '${result}'`);

    // Test 3: Verify side effect
    const count = s.get_count();
    if (count !== 1) {
        throw new Error(`Expected count=1, got ${count}`);
    }
    console.log(`3. get_count() = ${count}`);

    // Test 4: Call again
    result = s.handler_returns_computed();
    if (result !== "computed_2") {
        throw new Error(`Expected 'computed_2', got '${result}'`);
    }
    console.log(`4. handler_returns_computed() again = '${result}'`);

    console.log("PASS: System return behavior works correctly");
}

main();
