#!/usr/bin/env node
const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FRAMEC = path.join('framec','darwin','framec');
const FRM = path.join('sandbox','sim','AdapterStdioBreakpoints.frm');
const OUT_TS = path.join('sandbox','sim','gen','adapter_breakpoints.ts');
const OUT_JS = path.join('sandbox','sim','gen_js','sandbox','sim','gen','adapter_breakpoints.js');

function sh(cmd) { execSync(cmd, { stdio: 'inherit' }); }

function build() {
  fs.mkdirSync(path.dirname(OUT_TS), { recursive: true });
  fs.mkdirSync(path.join('sandbox','sim','gen_js'), { recursive: true });
  sh(`FRAME_EMIT_EXEC=1 ${FRAMEC} demo-frame -l typescript ${FRM} > ${OUT_TS}`);
  if (!fs.existsSync('frame_runtime_ts')) {
    sh(`cp -R /Users/marktruluck/projects/frame_transpiler/frame_runtime_ts frame_runtime_ts`);
  }
  sh(`npx -y tsc ${OUT_TS} frame_runtime_ts/index.ts --module commonjs --target ES2019 --outDir sandbox/sim/gen_js`);
}

function run() {
  const child = spawn('node', [OUT_JS], { stdio: ['pipe','pipe','inherit'] });
  let out = '';
  child.stdout.on('data', (d) => { out += d.toString(); });
  // Sequence: connected -> expect initialize + setBreakpoints, then ack, then ready, expect continue
  child.stdin.write(JSON.stringify({ type: 'event', event: 'connected' }) + '\n');
  setTimeout(() => {
    // Ack setBreakpoints
    child.stdin.write(JSON.stringify({ type: 'response', command: 'setBreakpoints', success: true }) + '\n');
    // Ready
    child.stdin.write(JSON.stringify({ type: 'event', event: 'ready' }) + '\n');
    // Terminated
    child.stdin.write(JSON.stringify({ type: 'event', event: 'terminated' }) + '\n');
    child.stdin.end();
  }, 50);
  child.on('exit', (code) => {
    const lines = out.trim().split('\n').map(s => s.trim());
    const first = lines[0];
    const second = lines[1];
    const expectedInit = JSON.stringify({ type: 'command', action: 'initialize', data: { stopOnEntry: false } });
    // We won’t assert exact setBreakpoints payload order beyond action name for brevity
    const hasSetBps = lines.some(l => { try { return JSON.parse(l).action === 'setBreakpoints'; } catch { return false; } });
    const hasContinue = lines.some(l => l === JSON.stringify({ type: 'command', action: 'continue' }));
    const pass = first === expectedInit && hasSetBps && hasContinue;
    if (pass) console.log('PASS adapter_breakpoints_ack');
    else {
      console.error('FAIL adapter_breakpoints_ack');
      console.error('got:', lines);
      process.exitCode = 1;
    }
  });
}

build();
run();

