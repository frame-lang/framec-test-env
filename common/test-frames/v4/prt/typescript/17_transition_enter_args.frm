@@target typescript

@@system TransitionEnterArgs {
    interface:
        start()
        get_log(): string[]

    domain:
        var log: string[] = []

    machine:
        $Idle {
            start() {
                this.log.push("idle:start");
                -> ("from_idle", 42) $Active
            }

            get_log(): string[] {
                return this.log;
            }
        }

        $Active {
            $>(source: string, value: number) {
                this.log.push(`active:enter:${source}:${value}`);
            }

            start() {
                this.log.push("active:start");
            }

            get_log(): string[] {
                return this.log;
            }
        }
}

function main() {
    console.log("=== Test 14: Transition Enter Args ===");
    const s = new TransitionEnterArgs();

    // Initial state is Idle
    let log = s.get_log();
    if (log.length !== 0) {
        throw new Error(`FAIL: Expected empty log, got ${log}`);
    }

    // Transition to Active with args
    s.start();
    log = s.get_log();
    if (!log.includes("idle:start")) {
        throw new Error(`FAIL: Expected 'idle:start' in log, got ${log}`);
    }
    if (!log.includes("active:enter:from_idle:42")) {
        throw new Error(`FAIL: Expected 'active:enter:from_idle:42' in log, got ${log}`);
    }
    console.log(`Log after transition: ${log}`);

    console.log("PASS: Transition enter args work correctly");
}

main();
