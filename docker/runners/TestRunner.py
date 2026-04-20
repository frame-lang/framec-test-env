#!/usr/bin/env python3
"""Single-process Python test dispatcher.

Reads a TSV manifest produced by python_batch.sh; for each RUN row, imports
the test module and captures its stdout/stderr. One interpreter cold start
covers the whole run.
"""
import importlib.util
import io
import os
import sys
import threading
import traceback


TIMEOUT_SEC = int(os.environ.get("PYTHON_TEST_TIMEOUT", "30"))


def run_one(module_path):
    """Import `module_path` with captured stdio; return (exit_code, output, timed_out)."""
    buf = io.StringIO()
    result = {"exc": None}

    def target():
        try:
            spec = importlib.util.spec_from_file_location(
                f"frametest_{os.path.basename(module_path)}", module_path,
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except SystemExit as e:
            if e.code not in (0, None):
                result["exc"] = e
        except BaseException as e:
            result["exc"] = e

    saved_out, saved_err = sys.stdout, sys.stderr
    sys.stdout = buf
    sys.stderr = buf
    try:
        t = threading.Thread(target=target, daemon=True)
        t.start()
        t.join(TIMEOUT_SEC)
        if t.is_alive():
            return 124, buf.getvalue(), True
    finally:
        sys.stdout = saved_out
        sys.stderr = saved_err

    if result["exc"] is not None:
        buf.write("\n")
        traceback.print_exception(type(result["exc"]), result["exc"], result["exc"].__traceback__, file=buf)
        return 1, buf.getvalue(), False
    return 0, buf.getvalue(), False


def report(test_num, test_name, code, output, timed_out):
    if timed_out:
        print(f"not ok {test_num} - {test_name} # TIMEOUT")
        return False
    if code != 0:
        print(f"not ok {test_num} - {test_name} # runtime error (exit {code})")
        for line in output.splitlines()[:5]:
            print(f"  # {line}")
        return False
    lines = output.splitlines()
    if any(l.startswith("not ok ") for l in lines):
        print(f"not ok {test_num} - {test_name}")
        return False
    if any(l.startswith("ok ") or "PASS" in l for l in lines):
        print(f"ok {test_num} - {test_name}")
        return True
    if not output.strip():
        print(f"ok {test_num} - {test_name} # clean exit")
        return True
    print(f"not ok {test_num} - {test_name} # unrecognized output")
    for line in lines[:3]:
        print(f"  # {line}")
    return False


def main(argv):
    if len(argv) < 2:
        print("usage: TestRunner.py <manifest.tsv>", file=sys.stderr)
        return 2
    manifest = argv[1]
    if not os.path.exists(manifest):
        print(f"manifest not found: {manifest}", file=sys.stderr)
        return 2

    pass_count = 0
    fail_count = 0
    skip_count = 0
    with open(manifest, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.rstrip("\n")
            if not raw.strip():
                continue
            parts = raw.split("\t")
            if len(parts) < 3:
                continue
            test_num, status, test_name = parts[0], parts[1], parts[2]
            main_path = parts[3] if len(parts) > 3 else ""
            extra = parts[4] if len(parts) > 4 else ""

            if status == "SKIP":
                print(f"ok {test_num} - {test_name} # SKIP")
                skip_count += 1
            elif status == "TRANSPILE_ERROR_OK":
                print(f"ok {test_num} - {test_name} # correctly rejected by transpiler")
                pass_count += 1
            elif status == "TRANSPILE_FAIL":
                print(f"not ok {test_num} - {test_name} # transpile failed")
                if extra:
                    for line in extra.split("\\n")[:5]:
                        print(f"  # {line}")
                fail_count += 1
            elif status == "NO_OUTPUT":
                print(f"not ok {test_num} - {test_name} # no output file")
                fail_count += 1
            elif status == "COMPILE_ONLY":
                print(f"ok {test_num} - {test_name} # transpiled")
                pass_count += 1
            elif status == "RUN":
                code, output, timed_out = run_one(main_path)
                if report(test_num, test_name, code, output, timed_out):
                    pass_count += 1
                else:
                    fail_count += 1
            else:
                print(f"not ok {test_num} - {test_name} # unknown status {status}")
                fail_count += 1
            sys.stdout.flush()

    print()
    print(f"# python: {pass_count} passed, {fail_count} failed, {skip_count} skipped")
    sys.stdout.flush()
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
