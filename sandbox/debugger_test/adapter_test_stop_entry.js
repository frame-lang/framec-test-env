#!/usr/bin/env node
const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FRAMEC = path.join('framec','darwin','framec');
const FRM = path.join('sandbox','sim','AdapterStdioStopEntry.frm');
const OUT_TS = path.join('sandbox','sim','gen','adapter_stop_entry.ts');
const OUT_JS = path.join('sandbox','sim','gen_js','sandbox','sim','gen','adapter_stop_entry.js');

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
  const inputs = [
    { type: 'event', event: 'connected' },
    { type: 'event', event: 'ready' },
    { type: 'event', event: 'stopped', data: { reason: 'entry' } },
    { type: 'event', event: 'terminated' }
  ];
  child.stdin.write(inputs.map(o => JSON.stringify(o)).join('\n') + '\n');
  child.stdin.end();
  child.on('exit', (code) => {
    const lines = out.trim().split('\n').map(s => s.trim());
    const expected0 = JSON.stringify({ type: 'command', action: 'initialize', data: { stopOnEntry: true } });
    const expected1 = JSON.stringify({ type: 'command', action: 'continue' });
    const pass = lines[0] === expected0 && lines.includes(expected1);
    if (pass) console.log('PASS adapter_stop_on_entry');
    else {
      console.error('FAIL adapter_stop_on_entry');
      console.error('got:', lines);
      console.error('want first:', expected0, ' then continue');
      process.exitCode = 1;
    }
  });
}

build();
run();

