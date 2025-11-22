const { spawn } = require('child_process');
const path = require('path');

function tee(prefix, src, dst) {
  src.on('data', (d) => {
    process.stdout.write(prefix + d.toString());
    dst.write(d);
  });
}

const adapterPath = path.join('sandbox','sim','gen_js','sandbox','sim','gen','adapter_out.js');
const pyClientPath = path.join('sandbox','protocol_harness','py_stdio_client.py');

const py = spawn('python3', [pyClientPath], { stdio: ['pipe','pipe','inherit'] });
const ts = spawn('node', [adapterPath], { stdio: ['pipe','pipe','inherit'] });

tee('[py->ts] ', py.stdout, ts.stdin);
tee('[ts->py] ', ts.stdout, py.stdin);

let done = false;
function finish(label, code){ if(done) return; done = true; console.log(`[bridge] ${label} exited ${code}`); try { py.kill('SIGKILL'); } catch(e) {} try { ts.kill('SIGKILL'); } catch(e) {} }
py.on('exit', (c)=>finish('py', c));
ts.on('exit', (c)=>finish('ts', c));
