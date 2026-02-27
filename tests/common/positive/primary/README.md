# V4 Primary Reference Tests

32 progressive tests validating V4 codegen across Python, TypeScript, and Rust.

## Test Sequence

| # | Test | Validates |
|---|------|-----------|
| 01 | minimal | Basic pipeline - compiles without error |
| 02 | interface | Interface method generation |
| 03 | transition | Handler + transition expansion |
| 04 | native_code | Native code preservation in handlers |
| 05 | enter_exit | Lifecycle handlers ($> and $<) |
| 06 | domain_vars | Domain variable initialization |
| 07 | params | Parameters to handlers |
| 08 | hsm | HSM parent forwarding (=> $^) |
| 09 | stack | Stack push/pop ($$[+]/$$[-]) |
| 10-12 | state_var_* | State variable preservation |
| 13-16 | system_return_* | System return semantics |
| 17-18 | transition_*_args | Enter/exit argument passing |
| 19 | transition_forward | Forward transitions (-> =>) |
| 20 | transition_pop | Pop transitions (-> $$[-]) |
| 21-22 | actions/operations | Action and operation blocks |
| 23-25 | persist_* | Serialization (@@persist) |
| 26 | state_params | State parameters ($State(args)) |
| 29 | forward_enter_first | Enter before forwarded event |
| 30 | hsm_default_forward | Default state-level forward (=> $^) |
| 31-34 | doc_* | Documentation examples |

## Running Tests

### Via Script (Recommended)
```bash
./run_tests.sh
```

### Via Docker
```bash
cd ../../..  # framepiler_test_env/
docker compose -f docker/docker-compose.yml up --build
```

## File Extensions

Each test has 3 versions:
- `XX_test_name.fpy` - Python
- `XX_test_name.fts` - TypeScript
- `XX_test_name.frs` - Rust

## Output

Tests emit TAP format:
```tap
TAP version 14
1..2
ok 1 - initial state is correct
ok 2 - transition works
```

## Pass Criteria

1. **Compiles**: Generated code passes language syntax check
2. **Runs**: Can instantiate class and call interface methods
3. **Passes**: Output contains "PASS" or all TAP tests pass
