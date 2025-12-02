#!/usr/bin/env python3
"""
Shared-env Stage 14 harness: IndentNormalizer sanity check.

This script mirrors the main repo's Stage 14 Phase A harness, but runs
entirely inside the shared test environment using the reference `framec`
binary under:

  bug/releases/frame_transpiler/<version>/framec/framec

It compiles the IndentNormalizer FRM from the main repo, builds a tiny
Rust binary that calls `IndentNormalizer::new().run()`, and asserts that
the normalized lines match the expected output for the hard-coded sample
handler body used in $ComputeBase.run().
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    shared_root = Path(__file__).resolve().parents[2]

    # Default to the latest known reference version; allow override via env.
    version = os.environ.get("FRAMEC_VERSION", "v0.86.63")
    framec_bin = (
        shared_root
        / "bug"
        / "releases"
        / "frame_transpiler"
        / version
        / "framec"
        / "framec"
    )

    if not framec_bin.is_file():
        print(f"ERROR: framec binary not found at {framec_bin}", file=sys.stderr)
        return 1

    # The IndentNormalizer FRM lives in the main repo. Expect its location
    # to be provided via FRAMEC_REPO_ROOT; default to ../frame_transpiler.
    repo_root = Path(
        os.environ.get(
            "FRAMEC_REPO_ROOT",
            str(shared_root.parent / "frame_transpiler"),
        )
    )
    frs = (
        repo_root
        / "framec"
        / "src"
        / "frame_c"
        / "v3"
        / "machines"
        / "indent_normalizer.frs"
    )
    if not frs.is_file():
        print(f"ERROR: IndentNormalizer FRM not found at {frs}", file=sys.stderr)
        return 1

    outdir = Path(tempfile.mkdtemp(prefix="indent_norm_shared_env_"))

    # Compile the Frame machine to Rust using the reference compiler.
    try:
        res = subprocess.run(
            [str(framec_bin), "compile", "-l", "rust", str(frs), "-o", str(outdir)],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print("ERROR: framec compile failed", file=sys.stderr)
        print(e.stdout, file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return 1

    rs_path = outdir / "indent_normalizer.rs"
    if not rs_path.is_file():
        print(f"ERROR: Expected generated Rust file at {rs_path}", file=sys.stderr)
        return 1

    # Build a small Rust harness that includes the generated module, seeds the
    # domain with the canonical sample handler body, and runs normalization.
    main_rs = outdir / "main.rs"
    main_rs.write_text(
        'include!("indent_normalizer.rs");\n\n'
        "fn main() {\n"
        "    let mut s = IndentNormalizer::new();\n"
        "    s.lines = vec![\n"
        "        \"        if self.stopOnEntry:\".to_string(),\n"
        "        \"            # Skip stop on entry if user continues\".to_string(),\n"
        "        \"            next_compartment = FrameCompartment(\\\"__S_state_Waiting\\\")\".to_string(),\n"
        "        \"            self._frame_transition(next_compartment)\".to_string(),\n"
        "        \"            return\".to_string(),\n"
        "        \"\".to_string(),\n"
        "    ];\n"
        "    s.flags_is_expansion = vec![false, false, true, true, false, false];\n"
        "    s.flags_is_comment = vec![false, true, false, false, false, false];\n"
        "    s.pad = \"        \".to_string();\n"
        "    s.run();\n"
        "}\n",
        encoding="utf-8",
    )

    bin_path = outdir / "indent_norm_bin"
    try:
        subprocess.run(
            ["rustc", "main.rs", "-O", "-o", str(bin_path)],
            cwd=str(outdir),
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print("ERROR: rustc failed for IndentNormalizer harness", file=sys.stderr)
        print(e.stdout, file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return 1

    # Run the harness and capture normalized lines.
    res = subprocess.run(
        [str(bin_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    lines = res.stdout.splitlines()

    expected = [
        "        if self.stopOnEntry:",
        "            # Skip stop on entry if user continues",
        "            next_compartment = FrameCompartment(\"__S_state_Waiting\")",
        "            self._frame_transition(next_compartment)",
        "            return",
        "        ",
    ]

    if lines != expected:
        print("ERROR: IndentNormalizer output mismatch", file=sys.stderr)
        print("Expected:", repr(expected), file=sys.stderr)
        print("Actual  :", repr(lines), file=sys.stderr)
        return 1

    print(
        f"Shared-env IndentNormalizer harness OK "
        f"(version={version}, repo_root={repo_root})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
