@@target typescript

@@system Minimal {
    interface:
        is_alive(): boolean

    machine:
        $Start {
            is_alive(): boolean {
                return true;
            }
        }
}

function main() {
    console.log("=== Test 01: Minimal System ===");
    const s = new Minimal();

    // Test that system instantiates and responds
    const result = s.is_alive();
    if (result !== true) {
        throw new Error(`Expected true, got ${result}`);
    }
    console.log(`is_alive() = ${result}`);

    console.log("PASS: Minimal system works correctly");
}

main();
