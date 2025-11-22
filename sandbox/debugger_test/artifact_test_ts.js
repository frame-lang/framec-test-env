#!/usr/bin/env node
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const { readAndExtract } = require('./lib/artifacts');

const FRAMEC = path.join('framec','darwin','framec');
const FRM = path.join('sandbox','v3_module','minimal_ts.frm');
const OUT = path.join('sandbox','v3_module','out.ts');

function compile() {
  execSync(`${FRAMEC} -l typescript --emit-debug ${FRM} > ${OUT}`, { stdio: 'inherit', shell: '/bin/bash' });
}
compile();
const { visitorMap: vmap, debugManifest: dman } = readAndExtract(OUT);
if (vmap && dman) {
  console.log('PASS artifact_trailers_ts');
} else {
  console.error('FAIL artifact_trailers_ts');
  process.exit(1);
}
