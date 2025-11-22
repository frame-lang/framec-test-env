#!/usr/bin/env python3
"""Unit test for rebuild RuntimeProtocol (no sockets).
Exercises handleCommand and sendMessage paths via a fake writer.
"""
import asyncio
import json
from typing import List

from runtime_protocol import RuntimeProtocol


class FakeWriter:
    def __init__(self, sink: List[str]):
        self._sink = sink

    def write(self, b: bytes):
        try:
            s = b.decode('utf-8')
        except Exception:  # pragma: no cover
            s = str(b)
        self._sink.append(s)

    async def drain(self):  # pragma: no cover
        return None

    def close(self):  # pragma: no cover
        pass

    async def wait_closed(self):  # pragma: no cover
        return None


async def run_async() -> None:
    rp = RuntimeProtocol()
    out: List[str] = []
    rp.writer = FakeWriter(out)

    # initialize should emit output then ready (and optional stopped(entry) when requested)
    await rp._action_handleCommand({"type": "command", "action": "initialize", "data": {"stopOnEntry": True}})
    assert any('\n' in s for s in out), 'expected newline-delimited output'
    evt_lines = [json.loads(s.strip()) for s in out if s.strip()]
    assert any(e.get('event') == 'output' for e in evt_lines), 'expected an output event after initialize'
    assert any(e.get('event') == 'ready' for e in evt_lines), 'expected a ready event after initialize'
    assert any(e.get('event') == 'stopped' and e.get('data', {}).get('reason') == 'entry' for e in evt_lines), 'expected stopped(entry) when stopOnEntry'

    # ping increments sequence and emits output
    seq_before = rp.sequence
    await rp._action_handleCommand({"type": "command", "action": "ping", "data": {}})
    assert rp.sequence == seq_before + 1, 'sequence should increment on ping'

    # setBreakpoints response then simulate 'next'/'continue'
    await rp._action_handleCommand({"type": "command", "action": "setBreakpoints", "data": {"lines": [12]}})
    await rp._action_handleCommand({"type": "command", "action": "next", "data": {}})
    await rp._action_handleCommand({"type": "command", "action": "continue", "data": {}})
    # terminate should emit terminated and set exitCode
    await rp._action_handleCommand({"type": "command", "action": "terminate", "data": {"exitCode": 42}})
    assert rp.exitCode == 42, 'exitCode should be set from terminate payload'
    evt_lines = [json.loads(s.strip()) for s in out if s.strip()]
    assert any(e.get('event') == 'terminated' for e in evt_lines), 'expected a terminated event'

    print('PASS test_runtime_protocol_unit')


def main() -> int:
    asyncio.run(run_async())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
