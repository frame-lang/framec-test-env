# Sandbox Fixtures (Shared Env)

This folder contains sandbox fixtures and harnesses migrated from the VS Code repo.
They are kept here to avoid generated or experimental files in the editor repo while
still providing reproducible fixtures for local and CI validation.

Included (sources only; no generated outputs):
- sim/: FRM fixtures and small JS helpers for adapter/runtime simulation
- protocol_harness/: stdio server/client harnesses (TS/JS/Python)
- debugger_test/: JS driver tests for adapter behavior (optional auxiliary checks)
- frame_test/, v3_module/, framec_demo/: small demo fixtures (outputs excluded)

Use the adapter_protocol harnesses for canonical checks:
- adapter_protocol/scripts/run_adapter_smoke.sh
- adapter_protocol/scripts/run_fda_smoke.sh
