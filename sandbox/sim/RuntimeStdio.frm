@@target python_3

@@system RuntimeStdio {
    machine:
        $Start {
            e() {
                import sys, json
                # Emit initial events
                sys.stdout.write(json.dumps({ 'type': 'event', 'event': 'connected' }) + "\n")
                sys.stdout.flush()
                
                # Read commands from stdin and respond
                for line in sys.stdin:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                    except Exception:
                        continue
                    if msg.get('type') == 'command':
                        action = msg.get('action')
                        if action == 'initialize':
                            sys.stdout.write(json.dumps({ 'type': 'event', 'event': 'ready' }) + "\n")
                            sys.stdout.flush()
                        elif action == 'continue':
                            sys.stdout.write(json.dumps({ 'type': 'event', 'event': 'terminated', 'data': { 'exitCode': 0 } }) + "\n")
                            sys.stdout.flush()
                            break
            }
        }
}

