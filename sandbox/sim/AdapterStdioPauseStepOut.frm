@@target typescript

@@system AdapterStdioPauseStepOut {
    machine:
        $Start {
            e() {
                let stepIssued: boolean = false;
                const readline = require('readline');
                const rl = readline.createInterface({ input: process.stdin });
                rl.on('line', (line: string) => {
                    line = line.trim();
                    if (!line) return;
                    try {
                        const msg = JSON.parse(line);
                        if (msg.type === 'event' && msg.event === 'connected') {
                            console.log(JSON.stringify({ type: 'command', action: 'initialize', data: { stopOnEntry: false } }));
                        } else if (msg.type === 'event' && msg.event === 'ready') {
                            console.log(JSON.stringify({ type: 'command', action: 'pause' }));
                        } else if (msg.type === 'event' && msg.event === 'stopped' && msg.data && msg.data.reason === 'pause') {
                            if (!stepIssued) {
                                stepIssued = true;
                                console.log(JSON.stringify({ type: 'command', action: 'stepOut' }));
                            }
                        } else if (msg.type === 'event' && msg.event === 'terminated') {
                            process.exit(0);
                        }
                    } catch {}
                });
            }
        }
}

