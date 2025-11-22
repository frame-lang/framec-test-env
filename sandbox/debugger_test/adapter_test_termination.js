#!/usr/bin/env node
const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FRAMEC = path.join('framec','darwin','framec');
const FRM = path.join('sandbox','sim','AdapterStdioTerminate.frm');
const OUT_TS = path.join('sandbox','sim','gen','adapter_terminate.ts');
const OUT_JS = path.join('sandbox','sim','gen_js','sandbox','sim','gen','adapter_terminate.js');

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
  const seq = [
    { type: 'event', event: 'connected' },
    { type: 'event', event: 'terminated' }
  ];
  child.stdin.write(seq.map(e => JSON.stringify(e)).join('\n') + '\n');
  child.stdin.end();
  child.on('exit', (code) => {
    const lines = out.trim().split('\n').map(s => s.trim());
    const expectedInit = JSON.stringify({ type: 'command', action: 'initialize', data: { stopOnEntry: false } });
    const pass = lines.length === 1 && lines[0] === expectedInit;
    if (pass) console.log('PASS adapter_termination_lifecycle');
    else {
      console.error('FAIL adapter_termination_lifecycle');
      console.error('got:', lines);
      process.exitCode = 1;
    }
  });
}

build();
run();

