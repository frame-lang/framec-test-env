#!/usr/bin/env node
// Minimal Node TCP server to validate newline-delimited JSON comms with Python.
// Usage: node ts_server.js

const net = require('net');
const { spawn } = require('child_process');

function startServer() {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      const port = address.port;
      console.log(`[server] listening on ${address.address}:${port}`);
      resolve({ server, port });
    });
  });
}

function startPythonClient(port) {
  const py = spawn('python3', [require('path').join(__dirname, 'py_client.py'), String(port)], {
    stdio: ['ignore', 'pipe', 'pipe'],
    env: process.env,
  });
  py.stdout.on('data', (d) => process.stdout.write(`[python] ${d}`));
  py.stderr.on('data', (d) => process.stderr.write(`[python:err] ${d}`));
  py.on('exit', (code) => console.log(`[python] exited ${code}`));
  return py;
}

function parseLines(socket, onJson) {
  let buf = '';
  socket.on('data', (chunk) => {
    buf += chunk.toString();
    let idx;
    while ((idx = buf.indexOf('\n')) >= 0) {
      const line = buf.slice(0, idx).trim();
      buf = buf.slice(idx + 1);
      if (!line) continue;
      try {
        const msg = JSON.parse(line);
        onJson(msg);
      } catch (e) {
        console.error('[server] failed to parse json line:', line);
      }
    }
  });
}

(async () => {
  const { server, port } = await startServer();

  server.on('connection', (socket) => {
    console.log('[server] client connected');
    parseLines(socket, (msg) => {
      console.log('[server] recv', msg);
      if (msg.type === 'event' && msg.event === 'connected') {
        // Send initialize command to exercise command path
        const cmd = { type: 'command', action: 'initialize', data: { stopOnEntry: false } };
        socket.write(JSON.stringify(cmd) + '\n');
      }
      if (msg.type === 'event' && msg.event === 'ready') {
        const cmd = { type: 'command', action: 'continue' };
        socket.write(JSON.stringify(cmd) + '\n');
      }
      if (msg.type === 'event' && msg.event === 'terminated') {
        console.log('[server] terminated received; closing');
        socket.end();
        server.close();
      }
    });
  });

  // Start the python client now that server is listening
  startPythonClient(port);
})();

