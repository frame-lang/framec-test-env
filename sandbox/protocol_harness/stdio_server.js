#!/usr/bin/env node
// Minimal stdio JSONL harness to validate TS↔Py comms without sockets.
// Usage: node stdio_server.js

const { spawn } = require('child_process');

function parseLines(stream, onLine) {
  let buf = '';
  stream.on('data', (chunk) => {
    buf += chunk.toString();
    let idx;
    while ((idx = buf.indexOf('\n')) >= 0) {
      const line = buf.slice(0, idx).trim();
      buf = buf.slice(idx + 1);
      if (line) onLine(line);
    }
  });
}

function send(child, obj) {
  const data = JSON.stringify(obj) + '\n';
  child.stdin.write(data);
}

(async () => {
  const py = spawn('python3', [require('path').join(__dirname, 'py_stdio_client.py')], {
    stdio: ['pipe', 'pipe', 'pipe'],
  });

  py.stderr.on('data', (d) => process.stderr.write(`[python:err] ${d}`));
  py.on('exit', (code) => console.log(`[python] exited ${code}`));

  parseLines(py.stdout, (line) => {
    try {
      const msg = JSON.parse(line);
      console.log('[server] recv', msg);
      if (msg.type === 'event' && msg.event === 'connected') {
        send(py, { type: 'command', action: 'initialize', data: { stopOnEntry: false } });
      } else if (msg.type === 'event' && msg.event === 'ready') {
        send(py, { type: 'command', action: 'continue' });
      } else if (msg.type === 'event' && msg.event === 'terminated') {
        console.log('[server] terminated, done');
        py.stdin.end();
      }
    } catch (e) {
      console.error('[server] parse error for line:', line);
    }
  });
})();

