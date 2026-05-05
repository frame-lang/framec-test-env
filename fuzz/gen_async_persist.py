#!/usr/bin/env python3
"""
Phase 26 — async × persist cross-product (canary).

Phase 6 (async) and Phase 2 (persist) are orthogonal at the
codegen level — async maps to the host-language coroutine
primitive, persist serializes domain + compartment chain. Their
intersection is small but real: a system can be both `async` (an
interface method awaits on something) and `@@[persist(...)]` (the
domain + state survive a save/restore round-trip).

The interesting edges:

1. **Save after async completes.** The host's coroutine runtime
   has finished; `_context_stack` is empty; save_state() must
   succeed. State machine state, domain, etc. round-trip
   normally.
2. **Save during async.** A handler that's awaiting has its
   activation frame on `_context_stack`; save_state() must
   refuse with E700 (quiescent contract). This isn't generated
   here — the matrix's tests/python/persist_quiescent fixtures
   cover it.

This generator exercises edge 1 — save-after-await and round-trip
through restore. Python-only first wave (canonical async target);
extension to TypeScript / JavaScript / Rust / C++ / Kotlin /
Swift / C# / Java / Dart follows the same template, mirroring
Phase 6's per-language renderer set.

Pattern:
  P1 await_then_save — single async fetch that mutates a domain
  field, then save outside the handler, restore, verify the field
  survived.

Usage:
  python3 gen_async_persist.py --max 5
"""
import argparse
from pathlib import Path


def gen_p1_python(case_id):
    tag = f"p1_await_then_save_{case_id}"
    return f'''@@[target("python_3")]

import asyncio


async def fetch_remote(key: str) -> str:
    # Mock async I/O. The point is that `await` is on the call
    # path; the value returned is what the system stores.
    await asyncio.sleep(0)
    return f"value-for-{{key}}"


@@[persist(str)]
@@[save(save_state)]
@@[load(restore_state)]
@@system Cache {{
    interface:
        async fetch(key: str): str
        get_last(): str

    machine:
        $Active {{
            fetch(key: str): str {{
                result = await fetch_remote(key)
                self.last = result
                @@:(result)
            }}
            get_last(): str {{ @@:(self.last) }}
        }}

    domain:
        last: str = ""
}}


async def main():
    c = Cache()
    v = await c.fetch("alice")
    if v != "value-for-alice":
        print(f"FAIL fetch: {{v}}")
        raise SystemExit(1)
    last_val = await c.get_last()
    if last_val != "value-for-alice":
        print(f"FAIL last: {{last_val}}")
        raise SystemExit(1)

    snap = c.save_state()
    fresh = Cache()
    fresh.restore_state(snap)
    fresh_last = await fresh.get_last()
    if fresh_last != "value-for-alice":
        print(f"FAIL post-restore: {{fresh_last}}")
        raise SystemExit(1)

    print("PASS: {tag}")


if __name__ == "__main__":
    asyncio.run(main())
'''


def write_cases(out_dir: Path, max_per_pattern):
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for i in range(max_per_pattern):
        case_id = f"{i:03d}"
        text = gen_p1_python(case_id)
        out = out_dir / f"python_3_p1_await_then_save_{case_id}.fpy"
        out.write_text(text)
        written += 1
    return written


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max", type=int, default=3,
                    help="Cases per pattern (default 3)")
    ap.add_argument("--out-dir", type=Path,
                    default=Path("cases_async_persist"),
                    help="Output directory")
    args = ap.parse_args()

    n = write_cases(args.out_dir, args.max)
    print(f"Wrote {n} cases to {args.out_dir}/")


if __name__ == "__main__":
    main()
