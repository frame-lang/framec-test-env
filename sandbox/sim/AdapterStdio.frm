@target typescript

system AdapterStdio {
    machine:
        $Start {
            e() {
                // Setup JSONL stdin reader; respond to runtime events
                const readline = require('readline');
                const rl = readline.createInterface({ input: process.stdin });
                rl.on('line', (line: string) => {
                    line = line.trim();
                    if (!line) return;
                    try {
                        const msg = JSON.parse(line);
                        // Basic handshake
                        if (msg.type === 'event' && msg.event === 'connected') {
                            console.log(JSON.stringify({ type: 'command', action: 'initialize', data: { stopOnEntry: false } }));
                        } else if (msg.type === 'event' && msg.event === 'ready') {
                            console.log(JSON.stringify({ type: 'command', action: 'continue' }));
                        } else if (msg.type === 'event' && msg.event === 'terminated') {
                            // End session
                            process.exit(0);
                        }
                    } catch (e) {
                        // ignore parse errors in demo
                    }
                });
            }
        }
}

