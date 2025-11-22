#!/usr/bin/env node
const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FRAMEC = path.join('framec','darwin','framec');
const FRM = path.join('sandbox','sim','AdapterStdioStepOut.frm');
const OUT_TS = path.join('sandbox','sim','gen','adapter_stepout.ts');
const OUT_JS = path.join('sandbox','sim','gen_js','sandbox','sim','gen','adapter_stepout.js');

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
  const events = [
    { type: 'event', event: 'connected' },
    { type: 'event', event: 'stopped', data: { reason: 'breakpoint' } },
    { type: 'event', event: 'continued' },
    { type: 'event', event: 'stopped', data: { reason: 'step' } },
    { type: 'event', event: 'terminated' }
  ];
  child.stdin.write(events.map(e => JSON.stringify(e)).join('\n') + '\n');
  child.stdin.end();
  child.on('exit', (code) => {
    const lines = out.trim().split('\n').map(s => s.trim());
    const init = JSON.stringify({ type: 'command', action: 'initialize', data: { stopOnEntry: false } });
    const stepOut = JSON.stringify({ type: 'command', action: 'stepOut' });
    const pass = lines[0] === init && lines.includes(stepOut);
    if (pass) console.log('PASS adapter_stepOut_single_inflight');
    else {
      console.error('FAIL adapter_stepOut_single_inflight');
      console.error('got:', lines);
      process.exitCode = 1;
    }
  });
}

build();
run();

