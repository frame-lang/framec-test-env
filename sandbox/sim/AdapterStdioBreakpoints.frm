@target typescript

system AdapterStdioBreakpoints {
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
                            console.log(JSON.stringify({ type: 'command', action: 'setBreakpoints', data: { lines: [12,24] } }));
                        } else if (msg.type === 'response' && msg.command === 'setBreakpoints' && msg.success === true) {
                            // wait for ready before continue
                        } else if (msg.type === 'event' && msg.event === 'ready') {
                            console.log(JSON.stringify({ type: 'command', action: 'continue' }));
                        } else if (msg.type === 'event' && msg.event === 'terminated') {
                            process.exit(0);
                        }
                    } catch {}
                });
            }
        }
}

