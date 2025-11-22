#!/usr/bin/env node
const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FRAMEC = path.join('framec','darwin','framec');
const FRM = path.join('sandbox','sim','AdapterStdioBpThenStep.frm');
const OUT_TS = path.join('sandbox','sim','gen','adapter_bp_then_step.ts');
const OUT_JS = path.join('sandbox','sim','gen_js','sandbox','sim','gen','adapter_bp_then_step.js');

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
  // Sequence: connected -> ack setBreakpoints -> ready -> stopped(bp) -> continued -> stopped(step) -> terminated
  child.stdin.write(JSON.stringify({ type: 'event', event: 'connected' }) + '\n');
  setTimeout(() => {
    child.stdin.write(JSON.stringify({ type: 'response', command: 'setBreakpoints', success: true }) + '\n');
    child.stdin.write(JSON.stringify({ type: 'event', event: 'ready' }) + '\n');
    child.stdin.write(JSON.stringify({ type: 'event', event: 'stopped', data: { reason: 'breakpoint' } }) + '\n');
    child.stdin.write(JSON.stringify({ type: 'event', event: 'continued' }) + '\n');
    child.stdin.write(JSON.stringify({ type: 'event', event: 'stopped', data: { reason: 'step' } }) + '\n');
    child.stdin.write(JSON.stringify({ type: 'event', event: 'terminated' }) + '\n');
    child.stdin.end();
  }, 50);
  child.on('exit', (code) => {
    const lines = out.trim().split('\n').map(s => s.trim());
    const init = JSON.stringify({ type: 'command', action: 'initialize', data: { stopOnEntry: false } });
    const hasInit = lines[0] === init;
    const hasSet = lines.some(l => { try { return JSON.parse(l).action === 'setBreakpoints'; } catch { return false; } });
    const nextCmd = JSON.stringify({ type: 'command', action: 'next' });
    const nextCount = lines.filter(l => l === nextCmd).length;
    const pass = hasInit && hasSet && nextCount === 1;
    if (pass) console.log('PASS adapter_bp_then_step_single_inflight');
    else {
      console.error('FAIL adapter_bp_then_step_single_inflight');
      console.error('got:', lines);
      process.exitCode = 1;
    }
  });
}

build();
run();

