@@target typescript

@@system SystemReturnReentrantTest {
    interface:
        outer_call(): string = "outer_default"
        inner_call(): string = "inner_default"
        nested_call(): string = "nested_default"
        get_log(): string

    machine:
        $Start {
            $.log: string = ""

            outer_call(): string {
                $.log = $.log + "outer_start,";
                const inner_result = this.inner_call();
                $.log = $.log + "outer_after_inner,";
                ^ "outer_result:" + inner_result
            }

            inner_call(): string {
                $.log = $.log + "inner,";
                ^ "inner_result"
            }

            nested_call(): string {
                $.log = $.log + "nested_start,";
                const result1 = this.inner_call();
                const result2 = this.outer_call();
                $.log = $.log + "nested_end,";
                ^ "nested:" + result1 + "+" + result2
            }

            get_log(): string {
                ^ $.log
            }
        }
}

function main(): void {
    console.log("=== Test 16: System Return Reentrant (TypeScript) ===");

    // Test 1: Simple inner call
    const s1 = new SystemReturnReentrantTest();
    let result = s1.inner_call();
    if (result !== "inner_result") {
        throw new Error(`Expected 'inner_result', got '${result}'`);
    }
    console.log(`1. inner_call() = '${result}'`);

    // Test 2: Outer calls inner
    const s2 = new SystemReturnReentrantTest();
    result = s2.outer_call();
    if (result !== "outer_result:inner_result") {
        throw new Error(`Expected 'outer_result:inner_result', got '${result}'`);
    }
    const log = s2.get_log();
    console.log(`2. outer_call() = '${result}'`);
    console.log(`   Log: '${log}'`);

    // Test 3: Deeply nested
    const s3 = new SystemReturnReentrantTest();
    result = s3.nested_call();
    const expected = "nested:inner_result+outer_result:inner_result";
    if (result !== expected) {
        throw new Error(`Expected '${expected}', got '${result}'`);
    }
    console.log(`3. nested_call() = '${result}'`);

    console.log("PASS: System return reentrant works correctly");
}

main();
