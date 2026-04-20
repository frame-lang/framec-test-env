#!/usr/bin/env node
// Single-process JS test dispatcher (ES module). Same shape as TestRunner.ts
// but without TS syntax — no transpiler needed.

import * as fs from 'fs'
import { pathToFileURL } from 'url'

const TIMEOUT_MS = (parseInt(process.env.JS_TEST_TIMEOUT || '30', 10) || 30) * 1000

async function main() {
  if (process.argv.length < 3) {
    process.stderr.write('usage: node TestRunner.mjs <manifest.tsv>\n')
    process.exit(2)
  }
  const manifest = process.argv[2]
  if (!fs.existsSync(manifest)) {
    process.stderr.write(`manifest not found: ${manifest}\n`)
    process.exit(2)
  }

  const lines = fs.readFileSync(manifest, 'utf8').split('\n').filter((l) => l.trim())
  let pass = 0, fail = 0, skip = 0

  for (const raw of lines) {
    const parts = raw.split('\t')
    if (parts.length < 3) continue
    const [testNum, status, testName] = parts
    const mainPath = parts[3] || ''
    const extra = parts[4] || ''

    switch (status) {
      case 'SKIP':
        console.log(`ok ${testNum} - ${testName} # SKIP`); skip++; break
      case 'TRANSPILE_ERROR_OK':
        console.log(`ok ${testNum} - ${testName} # correctly rejected by transpiler`); pass++; break
      case 'TRANSPILE_FAIL':
        console.log(`not ok ${testNum} - ${testName} # transpile failed`)
        if (extra) extra.split('\\n').slice(0, 5).forEach((l) => console.log('  # ' + l))
        fail++; break
      case 'NO_OUTPUT':
        console.log(`not ok ${testNum} - ${testName} # no output file`); fail++; break
      case 'COMPILE_ONLY':
        console.log(`ok ${testNum} - ${testName} # transpiled`); pass++; break
      case 'RUN': {
        const r = await runOne(mainPath)
        if (report(testNum, testName, r)) pass++
        else fail++
        break
      }
      default:
        console.log(`not ok ${testNum} - ${testName} # unknown status ${status}`); fail++
    }
  }

  console.log('')
  console.log(`# javascript: ${pass} passed, ${fail} failed, ${skip} skipped`)
  process.exit(fail === 0 ? 0 : 1)
}

async function runOne(modulePath) {
  const origStdout = process.stdout.write.bind(process.stdout)
  const origStderr = process.stderr.write.bind(process.stderr)
  const origExit = process.exit
  let buf = ''
  const capture = (chunk) => { buf += typeof chunk === 'string' ? chunk : chunk.toString('utf8'); return true }
  process.stdout.write = capture
  process.stderr.write = capture
  // Many generated tests end with `if (failures > 0) process.exit(1)`.
  // Letting that through kills the harness. Throw a sentinel instead and
  // translate it into an exit code for this test only.
  let exitCode = null
  process.exit = (c) => { exitCode = typeof c === 'number' ? c : 0; throw new Error('__test_exit__') }

  let code = 0, timedOut = false
  try {
    await Promise.race([
      import(pathToFileURL(modulePath).href),
      new Promise((_, rej) => setTimeout(() => { timedOut = true; rej(new Error('TIMEOUT')) }, TIMEOUT_MS)),
    ])
  } catch (e) {
    if (timedOut) code = 124
    else if (e?.message === '__test_exit__') code = exitCode ?? 1
    else { buf += '\n' + (e?.stack || String(e)); code = 1 }
  } finally {
    process.stdout.write = origStdout
    process.stderr.write = origStderr
    process.exit = origExit
  }
  return { exitCode: code, output: buf, timedOut }
}

function report(testNum, testName, r) {
  if (r.timedOut) { console.log(`not ok ${testNum} - ${testName} # TIMEOUT`); return false }
  if (r.exitCode !== 0) {
    console.log(`not ok ${testNum} - ${testName} # runtime error (exit ${r.exitCode})`)
    r.output.split('\n').slice(0, 5).forEach((l) => console.log('  # ' + l))
    return false
  }
  const ls = r.output.split('\n')
  if (ls.some((l) => l.startsWith('not ok '))) { console.log(`not ok ${testNum} - ${testName}`); return false }
  if (ls.some((l) => l.startsWith('ok ') || l.includes('PASS'))) { console.log(`ok ${testNum} - ${testName}`); return true }
  if (!r.output.trim()) { console.log(`ok ${testNum} - ${testName} # clean exit`); return true }
  console.log(`not ok ${testNum} - ${testName} # unrecognized output`)
  ls.slice(0, 3).forEach((l) => console.log('  # ' + l))
  return false
}

main().catch((e) => { process.stderr.write(`fatal: ${e?.stack || e}\n`); process.exit(2) })
