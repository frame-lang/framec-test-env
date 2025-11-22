#!/usr/bin/env python3
import json
import socket
import sys
import threading

def send(sock, obj):
    data = json.dumps(obj) + "\n"
    sock.sendall(data.encode('utf-8'))

def main():
    if len(sys.argv) < 2:
        print("usage: py_client.py <port>")
        sys.exit(2)

    port = int(sys.argv[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', port))

    # Reader thread to handle server commands
    stop = False
    def reader():
        nonlocal stop
        buf = ''
        while not stop:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk.decode('utf-8')
            while '\n' in buf:
                line, buf = buf.split('\n', 1)
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                    print(f"[client] recv {msg}")
                    # Minimal command handling to exercise comms
                    if msg.get('type') == 'command':
                        action = msg.get('action')
                        if action == 'initialize':
                            # Acknowledge initialize via 'ready'
                            send(s, { 'type': 'event', 'event': 'ready' })
                        elif action == 'continue':
                            # Immediately terminate
                            send(s, { 'type': 'event', 'event': 'terminated', 'data': { 'exitCode': 0 } })
                except Exception as e:
                    print(f"[client] parse error: {e}")

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    # Send initial connected event
    send(s, { 'type': 'event', 'event': 'connected' })

    # Wait for thread to finish
    t.join(timeout=2.0)
    stop = True
    try:
        s.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass
    s.close()

if __name__ == '__main__':
    main()

