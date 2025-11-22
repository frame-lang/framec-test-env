#!/usr/bin/env python3
"""
Stdio-based fake runtime for integration testing with AdapterProtocol.
Avoids TCP sockets; speaks newline-delimited JSON over stdin/stdout.
"""
import sys
import json

def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()

def main():
    # Signal connection
    send({"type": "event", "event": "connected"})
    seq = 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue
        if msg.get("type") != "command":
            continue
        action = msg.get("action")
        data = msg.get("data", {})
        if action == "initialize":
            # Emit hello to complete handshake, and an output event
            send({"type": "event", "event": "hello", "data": {"message": "runtime ready"}})
            send({"type": "event", "event": "output", "data": {"output": "Python runtime initialized\n", "category": "stdout"}})
            # Also emit ready and optional stopped(entry)
            send({"type": "event", "event": "ready"})
            if data.get("stopOnEntry"):
                send({"type": "event", "event": "stopped", "data": {"reason": "entry"}})
        elif action == "ping":
            seq += 1
            send({"type": "event", "event": "output", "data": {"output": f"Python pong #{seq}\n", "category": "stdout"}})
        elif action == "setBreakpoints":
            # Acknowledge breakpoint set and simulate an immediate breakpoint stop
            send({"type": "response", "command": "setBreakpoints", "success": True})
            send({"type": "event", "event": "stopped", "data": {"reason": "breakpoint", "threadId": 1}})
        elif action == "next":
            # Step Over: continued then stopped(step)
            send({"type": "event", "event": "continued"})
            send({"type": "event", "event": "stopped", "data": {"reason": "step", "threadId": 1}})
        elif action == "stepIn":
            send({"type": "event", "event": "continued"})
            send({"type": "event", "event": "stopped", "data": {"reason": "step", "threadId": 1}})
        elif action == "stepOut":
            send({"type": "event", "event": "continued"})
            send({"type": "event", "event": "stopped", "data": {"reason": "step", "threadId": 1}})
        elif action == "pause":
            send({"type": "event", "event": "stopped", "data": {"reason": "pause", "threadId": 1}})
        elif action == "raiseException":
            send({"type": "event", "event": "stopped", "data": {"reason": "exception", "message": "boom", "stack": "Traceback...", "threadId": 1}})
        elif action == "continue":
            # Emit continued then terminated for simple flow
            send({"type": "event", "event": "continued"})
            send({"type": "event", "event": "terminated", "data": {"exitCode": 0}})
            break
        elif action == "terminate":
            code = data.get("exitCode", 0)
            send({"type": "event", "event": "terminated", "data": {"exitCode": code}})
            break
        else:
            send({"type": "event", "event": "output", "data": {"output": f"Unhandled command: {action}\n", "category": "stderr"}})

if __name__ == '__main__':
    main()
