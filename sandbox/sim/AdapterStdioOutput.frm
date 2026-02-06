@@target typescript

@@system AdapterStdioOutput {
    machine:
        $Start {
            e() {
                const readline = require('readline');
                const rl = readline.createInterface({ input: process.stdin });
                rl.on('line', (line: string) => {
                    line = line.trim();
                    if (!line) return;
                    try {
                        const msg = JSON.parse(line);
                        if (msg.type === 'event' && msg.event === 'connected') {
                            console.log(JSON.stringify({ type: 'command', action: 'initialize', data: { stopOnEntry: false } }));
                        } else if (msg.type === 'event' && msg.event === 'output') {
                            // Pass-through output payload for verification
                            console.log(JSON.stringify(msg));
                        } else if (msg.type === 'event' && msg.event === 'terminated') {
                            process.exit(0);
                        }
                    } catch {}
                });
            }
        }
}

