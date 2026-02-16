@@target typescript

@@system TransitionExitArgs {
    interface:
        leave()
        get_log(): string[]

    domain:
        var log: string[] = []

    machine:
        $Active {
            $<(reason: string, code: number) {
                this.log.push(`exit:${reason}:${code}`);
            }

            leave() {
                this.log.push("leaving");
                ("cleanup", 42) -> $Done
            }

            get_log(): string[] {
                return this.log;
            }
        }

        $Done {
            $>() {
                this.log.push("enter:done");
            }

            get_log(): string[] {
                return this.log;
            }
        }
}

function main() {
    console.log("=== Test 15: Transition Exit Args ===");
    const s = new TransitionExitArgs();

    // Initial state is Active
    let log = s.get_log();
    if (log.length !== 0) {
        throw new Error(`Expected empty log, got ${log}`);
    }

    // Leave - should call exit handler with args
    s.leave();
    log = s.get_log();
    if (!log.includes("leaving")) {
        throw new Error(`Expected 'leaving' in log, got ${log}`);
    }
    if (!log.includes("exit:cleanup:42")) {
        throw new Error(`Expected 'exit:cleanup:42' in log, got ${log}`);
    }
    if (!log.includes("enter:done")) {
        throw new Error(`Expected 'enter:done' in log, got ${log}`);
    }
    console.log(`Log after transition: ${log}`);

    console.log("PASS: Transition exit args work correctly");
}

main();
