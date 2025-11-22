#!/usr/bin/env node
// Artifact test: compiles a minimal Py V3 module with --emit-debug and parses trailers

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const { readAndExtract } = require('./lib/artifacts');

const FRAMEC = path.join('framec','darwin','framec');
const FRM = path.join('sandbox','v3_module','minimal_py.frm');
const OUT = path.join('sandbox','v3_module','out.py');

function sh(cmd, opts={}) { execSync(cmd, { stdio: 'pipe', ...opts }); }

function compileModule() {
  const cmd = `${FRAMEC} -l python_3 --emit-debug ${FRM} > ${OUT}`;
  execSync(cmd, { stdio: 'inherit', shell: '/bin/bash' });
}

function run() {
  compileModule();
  const { visitorMap: vmap, debugManifest: dman, frameMap: fmap } = readAndExtract(OUT);
  const pass = vmap && dman && fmap && vmap.schemaVersion >= 1 && dman.schemaVersion >= 1;
  if (pass) {
    console.log('PASS artifact_trailers');
  } else {
    console.error('FAIL artifact_trailers');
    console.error('visitor-map:', vmap);
    console.error('debug-manifest:', dman);
    console.error('frame-map:', fmap);
    process.exitCode = 1;
  }
}

run();
