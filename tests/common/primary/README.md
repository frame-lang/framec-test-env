# V4 PRT Test Suite

Progressive tests for validating V4 codegen across Python, Rust, and TypeScript.

## Test Sequence

| # | Test | Validates | Task |
|---|------|-----------|------|
| 01 | minimal | Basic pipeline - compiles without error | #8 |
| 02 | interface | Interface method generation | #9 |
| 03 | transition | Handler + transition expansion | #10,11,12 |
| 04 | native_code | Native code preservation in handlers | #10,11,12 |
| 05 | enter_exit | Lifecycle handlers ($> and $<) | #10,11,12 |
| 06 | domain_vars | Domain variable initialization | #10,11,12 |
| 07 | params | Parameters to handlers | #10,11,12 |
| 08 | hsm | HSM parent forwarding (=> $^) | #10,11,12 |
| 09 | stack | Stack push/pop ($$[+]/$$[-]) | #10,11,12 |

## Running Tests

### Compile All Languages

```bash
# Set up
export TEST_DIR=/Users/marktruluck/projects/frame_transpiler/framepiler_test_env/common/test-frames/v4/prt
export FRAMEC=/Users/marktruluck/projects/frame_transpiler/target/release/framec

# Run for each test
for test in 01_minimal 02_interface 03_transition 04_native_code 05_enter_exit 06_domain_vars 07_params 08_hsm 09_stack; do
    echo "=== Testing $test ==="

    # Python
    FRAME_USE_V4=1 $FRAMEC $TEST_DIR/${test}.frm -l python_3 -o /tmp/${test}.py
    python3 -m py_compile /tmp/${test}.py && echo "  Python: SYNTAX OK" || echo "  Python: SYNTAX FAIL"

    # TypeScript
    FRAME_USE_V4=1 $FRAMEC $TEST_DIR/${test}.frm -l typescript -o /tmp/${test}.ts
    npx tsc --noEmit /tmp/${test}.ts 2>/dev/null && echo "  TypeScript: SYNTAX OK" || echo "  TypeScript: SYNTAX FAIL"

    # Rust
    FRAME_USE_V4=1 $FRAMEC $TEST_DIR/${test}.frm -l rust -o /tmp/${test}.rs
    rustc --emit=metadata /tmp/${test}.rs 2>/dev/null && echo "  Rust: SYNTAX OK" || echo "  Rust: SYNTAX FAIL"
done
```

### Validate Individual Test

```bash
# Python
FRAME_USE_V4=1 $FRAMEC 03_transition.frm -l python_3 -o /tmp/test.py
python3 -c "
from test import WithTransition
t = WithTransition()
t.next()  # Should print 'Going to Second'
t.next()  # Should print 'Going to First'
"

# TypeScript
FRAME_USE_V4=1 $FRAMEC 03_transition.frm -l typescript -o /tmp/test.ts
npx ts-node -e "
import { WithTransition } from '/tmp/test';
const t = new WithTransition();
t.next();  // Should print 'Going to Second'
t.next();  // Should print 'Going to First'
"

# Rust
FRAME_USE_V4=1 $FRAMEC 03_transition.frm -l rust -o /tmp/test.rs
# Compile and run (requires main function wrapper)
```

## Expected Output Structure

All three languages should produce equivalent structures:

### Class/Struct
- State tracking: `_state`, `_state_stack`, `_state_context`
- Constructor initializes to first state

### Methods
- **Interface methods** (public): `greet()`, `next()`, etc.
- **Handler methods** (private): `_s_Ready_greet()`, `_s_First_next()`, etc.
- **Lifecycle handlers**: `_s_Off_enter()`, `_s_Off_exit()`
- **Core machinery**: `_transition()`, `_dispatch_event()`, `_enter()`, `_exit()`

## Pass Criteria

1. **Syntax Valid**: Generated code passes language syntax check
2. **Runnable**: Can instantiate class and call interface methods
3. **Correct Behavior**: Output matches expected behavior
