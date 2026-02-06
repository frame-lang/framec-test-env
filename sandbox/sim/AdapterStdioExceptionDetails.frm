@@target typescript

@@system AdapterStdioExceptionDetails {
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
                        } else if (msg.type === 'event' && msg.event === 'stopped' && msg.data && msg.data.reason === 'exception') {
                            // Echo the exception payload for verification and then continue
                            console.log(JSON.stringify({ type: 'exception', message: msg.data.message, stack: msg.data.stack }));
                            console.log(JSON.stringify({ type: 'command', action: 'continue' }));
                        } else if (msg.type === 'event' && msg.event === 'terminated') {
                            process.exit(0);
                        }
                    } catch {}
                });
            }
        }
}

