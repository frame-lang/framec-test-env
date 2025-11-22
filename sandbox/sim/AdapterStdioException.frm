@target typescript

system AdapterStdioException {
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
                        } else if (msg.type === 'event' && msg.event === 'exception') {
                            // Not part of the minimal path, but echo and continue for test coverage
                            console.log(JSON.stringify(msg));
                            console.log(JSON.stringify({ type: 'command', action: 'continue' }));
                        } else if (msg.type === 'event' && msg.event === 'stopped' && msg.data && msg.data.reason === 'exception') {
                            console.log(JSON.stringify({ type: 'command', action: 'continue' }));
                        } else if (msg.type === 'event' && msg.event === 'terminated') {
                            process.exit(0);
                        }
                    } catch {}
                });
            }
        }
}

