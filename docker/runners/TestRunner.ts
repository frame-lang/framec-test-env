#!/usr/bin/env tsx
// Single-process TypeScript test dispatcher.
//
// TypeScript tests are modules with top-level driver code. Dynamic import()
// executes that driver; its stdout/stderr are captured via a write shim.
// One tsx cold start covers the whole run — vs. per-test today.

import * as fs from 'fs'
import { pathToFileURL } from 'url'

const TIMEOUT_MS = (parseInt(process.env.TS_TEST_TIMEOUT || '30', 10) || 30) * 1000

async function main() {
  if (process.argv.length < 3) {
    process.stderr.write('usage: tsx TestRunner.ts <manifest.tsv>\n')
    process.exit(2)
  }
  const manifest = process.argv[2]
  if (!fs.existsSync(manifest)) {
    process.stderr.write(`manifest not found: ${manifest}\n`)
    process.exit(2)
  }

  const lines = fs.readFileSync(manifest, 'utf8').split('\n').filter((l) => l.trim().length > 0)
  let pass = 0
  let fail = 0
  let skip = 0

  for (const raw of lines) {
    const parts = raw.split('\t')
    if (parts.length < 3) continue
    const [testNum, status, testName] = parts
    const mainPath = parts[3] || ''
    const extra = parts[4] || ''

    switch (status) {
      case 'SKIP':
        console.log(`ok ${testNum} - ${testName} # SKIP`)
        skip++
        break
      case 'TRANSPILE_ERROR_OK':
        console.log(`ok ${testNum} - ${testName} # correctly rejected by transpiler`)
        pass++
        break
      case 'TRANSPILE_FAIL':
        console.log(`not ok ${testNum} - ${testName} # transpile failed`)
        if (extra) {
          for (const line of extra.split('\\n').slice(0, 5)) {
            console.log('  # ' + line)
          }
        }
        fail++
        break
      case 'NO_OUTPUT':
        console.log(`not ok ${testNum} - ${testName} # no output file`)
        fail++
        break
      case 'COMPILE_ONLY':
        console.log(`ok ${testNum} - ${testName} # transpiled`)
        pass++
        break
      case 'RUN': {
        const result = await runOne(mainPath)
        if (reportResult(testNum, testName, result)) pass++
        else fail++
        break
      }
      default:
        console.log(`not ok ${testNum} - ${testName} # unknown status ${status}`)
        fail++
    }
  }

  console.log('')
  console.log(`# typescript: ${pass} passed, ${fail} failed, ${skip} skipped`)
  process.exit(fail === 0 ? 0 : 1)
}

interface TestResult {
  exitCode: number
  output: string
  timedOut: boolean
}

async function runOne(modulePath: string): Promise<TestResult> {
  const origStdout = process.stdout.write.bind(process.stdout)
  const origStderr = process.stderr.write.bind(process.stderr)
  let buf = ''
  const capture = (chunk: any) => {
    buf += typeof chunk === 'string' ? chunk : chunk.toString('utf8')
    return true
  }
  process.stdout.write = capture as any
  process.stderr.write = capture as any

  let code = 0
  let timedOut = false
  try {
    await Promise.race([
      import(pathToFileURL(modulePath).href),
      new Promise((_, rej) =>
        setTimeout(() => {
          timedOut = true
          rej(new Error('TIMEOUT'))
        }, TIMEOUT_MS),
      ),
    ])
  } catch (e: any) {
    if (timedOut) {
      code = 124
    } else {
      buf += '\n' + (e?.stack || String(e))
      code = 1
    }
  } finally {
    process.stdout.write = origStdout
    process.stderr.write = origStderr
  }
  return { exitCode: code, output: buf, timedOut }
}

function reportResult(testNum: string, testName: string, r: TestResult): boolean {
  if (r.timedOut) {
    console.log(`not ok ${testNum} - ${testName} # TIMEOUT`)
    return false
  }
  if (r.exitCode !== 0) {
    console.log(`not ok ${testNum} - ${testName} # runtime error (exit ${r.exitCode})`)
    emitLines(r.output, 5)
    return false
  }
  const lines = r.output.split('\n')
  if (lines.some((l) => l.startsWith('not ok '))) {
    console.log(`not ok ${testNum} - ${testName}`)
    return false
  }
  if (lines.some((l) => l.startsWith('ok ') || l.includes('PASS'))) {
    console.log(`ok ${testNum} - ${testName}`)
    return true
  }
  if (r.output.trim().length === 0) {
    console.log(`ok ${testNum} - ${testName} # clean exit`)
    return true
  }
  console.log(`not ok ${testNum} - ${testName} # unrecognized output`)
  emitLines(r.output, 3)
  return false
}

function emitLines(s: string, max: number) {
  let n = 0
  for (const line of s.split('\n')) {
    if (n >= max) break
    console.log('  # ' + line)
    n++
  }
}

main().catch((e) => {
  process.stderr.write(`fatal: ${e?.stack || e}\n`)
  process.exit(2)
})
