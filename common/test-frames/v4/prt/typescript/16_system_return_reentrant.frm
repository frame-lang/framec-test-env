@@target typescript

// Tests that nested interface calls maintain separate return contexts

@@system SystemReturnReentrantTest {
    interface:
        outer_call(): string
        inner_call(): string
        nested_call(): string
        get_log(): string

    machine:
        $Start {
            $.log: string = ""

            outer_call(): string {
                $.log = $.log + "outer_start,"
                // Call inner method - this creates nested return context
                const inner_result: string = this.inner_call()
                $.log = $.log + "outer_after_inner,"
                // Our return should be independent of inner's return
                return "outer_result:" + inner_result
            }

            inner_call(): string {
                $.log = $.log + "inner,"
                return "inner_result"
            }

            nested_call(): string {
                $.log = $.log + "nested_start,"
                // Two levels of nesting
                const result1: string = this.inner_call()
                const result2: string = this.outer_call()
                $.log = $.log + "nested_end,"
                return "nested:" + result1 + "+" + result2
            }

            get_log(): string {
                return $.log
            }
        }
}

function main(): void {
    console.log("=== Test 16: System Return Reentrant (Nested Calls) (TypeScript) ===");

    // Test 1: Simple inner call
    const s1 = new SystemReturnReentrantTest();
    let result = s1.inner_call();
    if (result !== "inner_result") {
        throw new Error(`Expected 'inner_result', got '${result}'`);
    }
    console.log(`1. inner_call() = '${result}'`);

    // Test 2: Outer calls inner - return contexts should be separate
    const s2 = new SystemReturnReentrantTest();
    result = s2.outer_call();
    if (result !== "outer_result:inner_result") {
        throw new Error(`Expected 'outer_result:inner_result', got '${result}'`);
    }
    const log = s2.get_log();
    if (!log.includes("outer_start")) {
        throw new Error(`Missing outer_start in log: ${log}`);
    }
    if (!log.includes("inner")) {
        throw new Error(`Missing inner in log: ${log}`);
    }
    if (!log.includes("outer_after_inner")) {
        throw new Error(`Missing outer_after_inner in log: ${log}`);
    }
    console.log(`2. outer_call() = '${result}'`);
    console.log(`   Log: '${log}'`);

    // Test 3: Deeply nested calls
    const s3 = new SystemReturnReentrantTest();
    result = s3.nested_call();
    const expected = "nested:inner_result+outer_result:inner_result";
    if (result !== expected) {
        throw new Error(`Expected '${expected}', got '${result}'`);
    }
    console.log(`3. nested_call() = '${result}'`);

    console.log("PASS: System return reentrant (nested calls) works correctly");
}

main();
