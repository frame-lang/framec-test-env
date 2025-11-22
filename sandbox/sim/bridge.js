const { spawn } = require('child_process');
const fs = require('fs');
function pump(src, dst) {
  src.on('data', (d) => {
    dst.write(d);
  });
}
const py = spawn('python3', ['sandbox/sim/gen/runtime_out.py'], { stdio: ['pipe','pipe','inherit'] });
const ts = spawn('node', ['sandbox/sim/gen_js/sandbox/sim/gen/adapter_out.js'], { stdio: ['pipe','pipe','inherit'] });
// Cross-wire
pump(py.stdout, ts.stdin);
pump(ts.stdout, py.stdin);
// Exit when either ends
let done = false;
function finish(code,label){ if(done) return; done=true; console.log(`[bridge] ${label} exited ${code}`); py.kill('SIGKILL'); ts.kill('SIGKILL'); }
py.on('exit',(c)=>finish(c,'py'));
ts.on('exit',(c)=>finish(c,'ts'));
