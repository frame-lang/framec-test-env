@@target typescript

@@system SystemReturnDefaultTest {
    interface:
        get_status(): string = "unknown"
        get_count(): number = -1
        no_default(): string
        handler_sets_value(): string = "default"

    machine:
        $Start {
            get_status(): string {
                // No return - should use default "unknown"
            }

            get_count(): number {
                // No return - should use default -1
            }

            no_default(): string {
                // No default specified - should return null
            }

            handler_sets_value(): string {
                ^ "handler_value"
            }
        }
}

function main(): void {
    console.log("=== Test 14: System Return Default Values (TypeScript) ===");
    const s = new SystemReturnDefaultTest();

    // Test 1: String default
    let result: string = s.get_status();
    if (result !== "unknown") {
        throw new Error(`Expected 'unknown', got '${result}'`);
    }
    console.log(`1. get_status() (no handler set) = '${result}'`);

    // Test 2: Number default
    let count: number = s.get_count();
    if (count !== -1) {
        throw new Error(`Expected -1, got ${count}`);
    }
    console.log(`2. get_count() (no handler set) = ${count}`);

    // Test 3: No default - should return null
    let noDefault: string = s.no_default();
    if (noDefault !== null) {
        throw new Error(`Expected null, got '${noDefault}'`);
    }
    console.log(`3. no_default() = ${noDefault}`);

    // Test 4: Handler sets value
    result = s.handler_sets_value();
    if (result !== "handler_value") {
        throw new Error(`Expected 'handler_value', got '${result}'`);
    }
    console.log(`4. handler_sets_value() = '${result}'`);

    console.log("PASS: System return default values work correctly");
}

main();
