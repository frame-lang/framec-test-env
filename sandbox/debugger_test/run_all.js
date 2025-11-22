#!/usr/bin/env node
const { execFileSync } = require('child_process');
const path = require('path');

const tests = [
  'adapter_test.js',
  'adapter_test_stop_entry.js',
  'adapter_test_breakpoints.js',
  'adapter_test_bp_then_step.js',
  'adapter_test_step.js',
  'adapter_test_stepin.js',
  'adapter_test_stepout.js',
  'adapter_test_output.js',
  'adapter_test_multiple_stops_single_inflight.js',
  'adapter_test_pause.js',
  'adapter_test_pause_then_stepin.js',
  'adapter_test_pause_then_stepout.js',
  'adapter_test_pause_then_step.js',
  'adapter_test_exception.js',
  'adapter_test_exception_details.js',
  'artifact_test.js',
  'adapter_test_termination.js'
];

let failures = 0;
for (const t of tests) {
  const p = path.join(__dirname, t);
  try {
    execFileSync('node', [p], { stdio: 'inherit' });
  } catch (e) {
    failures++;
  }
}
if (failures) {
  console.error(`FAIL ${failures}/${tests.length} tests`);
  process.exit(1);
} else {
  console.log(`PASS all ${tests.length} tests`);
}
