Debugger Test Path (Sandbox)

This sandbox validates two parts of the debugger path using the V3 toolchain:

- Adapter handshake (TS) over stdio using a minimal Frame module compiled via demo-frame.
- Module artifact generation (non-demo compile) and trailer parsing for Py target.

Run tests
- Adapter handshake: `node sandbox/debugger_test/adapter_test.js`
- Artifact check: `node sandbox/debugger_test/artifact_test.js`

Prereqs
- framec 0.86.27+ at `framec/darwin/framec`
- Node + TypeScript (`npx tsc` available)

