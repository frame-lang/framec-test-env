@@target typescript

@@system AdapterStdioBpThenStep {
    machine:
        $Start {
            e() {
                let inFlight: boolean = false;
                const readline = require('readline');
                const rl = readline.createInterface({ input: process.stdin });
                rl.on('line', (line: string) => {
                    line = line.trim();
                    if (!line) return;
                    try {
                        const msg = JSON.parse(line);
                        if (msg.type === 'event' && msg.event === 'connected') {
                            console.log(JSON.stringify({ type: 'command', action: 'initialize', data: { stopOnEntry: false } }));
                            console.log(JSON.stringify({ type: 'command', action: 'setBreakpoints', data: { lines: [12] } }));
                        } else if (msg.type === 'response' && msg.command === 'setBreakpoints' && msg.success === true) {
                            // wait for ready
                        } else if (msg.type === 'event' && msg.event === 'ready') {
                            // idle until breakpoint
                        } else if (msg.type === 'event' && msg.event === 'stopped' && msg.data && msg.data.reason === 'breakpoint') {
                            if (!inFlight) {
                                inFlight = true;
                                console.log(JSON.stringify({ type: 'command', action: 'next' }));
                            }
                        } else if (msg.type === 'event' && msg.event === 'continued') {
                            inFlight = false;
                        } else if (msg.type === 'event' && msg.event === 'terminated') {
                            process.exit(0);
                        }
                    } catch {}
                });
            }
        }
}

