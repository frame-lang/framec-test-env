#!/usr/bin/env python3
import sys
import json

def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()

def main():
    # Emit connected right away
    send({ 'type': 'event', 'event': 'connected' })

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception as e:
            print(f"[client] parse error: {e}", file=sys.stderr)
            continue
        if msg.get('type') == 'command':
            action = msg.get('action')
            if action == 'initialize':
                send({ 'type': 'event', 'event': 'ready' })
            elif action == 'continue':
                send({ 'type': 'event', 'event': 'terminated', 'data': { 'exitCode': 0 } })
                break

if __name__ == '__main__':
    main()

