This folder is the canonical bug tracker for the Framepiler shared test environment.

- Source migrated from /Users/marktruluck/projects/frame_transpiler/docs/bugs
- Structure (single-folder model):
  - bugs/ — all bug files live here
  - INDEX.md — grouped views built from each bug file’s `status` metadata
  - BUG_TRACKING_POLICY.md — process and state transitions
- Policy: see BUG_TRACKING_POLICY.md (no per‑state subfolders; status lives in metadata)
- Preferred validation: shared adapter smoke
  FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec \
    /Users/marktruluck/projects/framepiler_test_env/adapter_protocol/scripts/run_adapter_smoke.sh

How to add a bug
1) Pick next number from INDEX.md
2) Copy TEMPLATE.md to `bugs/bug_NNN_short_title.md`
3) Fill metadata + sections; set `status: Open`, add repro + validators
4) Update INDEX.md counts and tables (scan bugs/ by status)

State transitions (metadata only)
- Open → Fixed (developer sets `status: Fixed` + `fixed_version`)
- Fixed → Closed (opener verifies; sets `status: Closed`)
- Closed/Fixed → Reopen (regression; sets `status: Reopen` + Work Log reason), then back through Fixed → Closed
