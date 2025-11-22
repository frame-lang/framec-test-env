#!/usr/bin/env node
// Adapter handshake test: compiles AdapterStdio.frm (TS) and exercises JSONL handshake.

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const FRAMEC = path.join('framec','darwin','framec');
const ADAPTER_FRM = path.join('sandbox','sim','AdapterStdio.frm');
const OUT_TS = path.join('sandbox','sim','gen','adapter_out.ts');
const OUT_JS = path.join('sandbox','sim','gen_js','sandbox','sim','gen','adapter_out.js');

function sh(cmd, opts={}) { execSync(cmd, { stdio: 'inherit', ...opts }); }

function buildAdapter() {
  fs.mkdirSync(path.dirname(OUT_TS), { recursive: true });
  fs.mkdirSync(path.join('sandbox','sim','gen_js'), { recursive: true });
  sh(`FRAME_EMIT_EXEC=1 ${FRAMEC} demo-frame -l typescript ${ADAPTER_FRM} > ${OUT_TS}`);
  // Ensure TS runtime is available for import
  if (!fs.existsSync('frame_runtime_ts')) {
    sh(`cp -R /Users/marktruluck/projects/frame_transpiler/frame_runtime_ts frame_runtime_ts`);
  }
  // Compile TS -> JS
  sh(`npx -y tsc ${OUT_TS} frame_runtime_ts/index.ts --module commonjs --target ES2019 --outDir sandbox/sim/gen_js`);
}

function runTest() {
  const child = spawn('node', [OUT_JS], { stdio: ['pipe','pipe','inherit'] });
  let stdout = '';
  child.stdout.on('data', (d) => { stdout += d.toString(); });
  const lines = [
    { type: 'event', event: 'connected' },
    { type: 'event', event: 'ready' },
    { type: 'event', event: 'terminated' }
  ];
  child.stdin.write(lines.map(l => JSON.stringify(l)).join('\n') + '\n');
  setTimeout(() => child.stdin.end(), 50);

  child.on('exit', (code) => {
    const outLines = stdout.trim().split('\n').map(s => s.trim()).filter(Boolean);
    const expected = [
      JSON.stringify({ type: 'command', action: 'initialize', data: { stopOnEntry: false } }),
      JSON.stringify({ type: 'command', action: 'continue' })
    ];
    const pass = outLines[0] === expected[0] && outLines[1] === expected[1];
    if (pass) {
      console.log('PASS adapter_handshake');
    } else {
      console.error('FAIL adapter_handshake');
      console.error('got :', outLines);
      console.error('want:', expected);
      process.exitCode = 1;
    }
  });
}

buildAdapter();
runTest();

