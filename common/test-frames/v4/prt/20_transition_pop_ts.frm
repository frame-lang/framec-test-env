@@target typescript

@@system TransitionPopTest {
    interface:
        start()
        process()
        get_state(): string
        get_log(): string[]

    domain:
        var log: string[] = []

    machine:
        $Idle {
            start() {
                this.log.push("idle:start:push");
                `push$
                -> $Working
            }

            process() {
                this.log.push("idle:process");
            }

            get_state(): string {
                return "Idle";
            }

            get_log(): string[] {
                return this.log;
            }
        }

        $Working {
            process() {
                this.log.push("working:process:before_pop");
                -> pop$
                // This should NOT execute because pop transitions away
                this.log.push("working:process:after_pop");
            }

            get_state(): string {
                return "Working";
            }

            get_log(): string[] {
                return this.log;
            }
        }
}

function main(): void {
    console.log("=== Test 17: Transition Pop (TypeScript) ===");
    const s = new TransitionPopTest();

    // Initial state should be Idle
    if (s.get_state() !== "Idle") throw new Error(`Expected 'Idle', got '${s.get_state()}'`);
    console.log(`Initial state: ${s.get_state()}`);

    // start() pushes Idle, transitions to Working
    s.start();
    if (s.get_state() !== "Working") throw new Error(`Expected 'Working', got '${s.get_state()}'`);
    console.log(`After start(): ${s.get_state()}`);

    // process() in Working does pop transition back to Idle
    s.process();
    if (s.get_state() !== "Idle") throw new Error(`Expected 'Idle' after pop, got '${s.get_state()}'`);
    console.log(`After process() with pop: ${s.get_state()}`);

    const log = s.get_log();
    console.log(`Log: ${JSON.stringify(log)}`);

    // Verify log contents
    if (!log.includes("idle:start:push")) throw new Error("Expected 'idle:start:push' in log");
    if (!log.includes("working:process:before_pop")) throw new Error("Expected 'working:process:before_pop' in log");
    if (log.includes("working:process:after_pop")) throw new Error("Should NOT have 'working:process:after_pop' in log");

    console.log("PASS: Transition pop works correctly");
}

main();
