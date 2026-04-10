# Erlang Backend Bug Report

**Binary**: framec 4.0.0
**Current results**: 132 pass, 0 fail, 4 skip
**Previous (compile-only)**: 131 pass, 0 fail, 5 skip

Bugs 1-3 have been fixed. The escript-based execution harness now runs all non-skipped tests.
Issues 4-5 are open — they require backend features to resolve.

## Bug 1: Variable rebinding in return paths

**Tests**: comparison_ops, equality, logical_ops, ternary_expr
**Severity**: High — affects all `@@:return` patterns with conditionals

Erlang uses single-assignment variables. The generated code binds `__ReturnVal` then attempts to rebind it in conditional branches:

```erlang
active({call, From}, {is_greater, A, B}, Data) ->
    __ReturnVal = undefined,        %% first binding
    case (A > B) of
    true ->
        __ReturnVal = true,         %% ILLEGAL: rebinding
        return                      %% ILLEGAL: bare atom, not valid here
    ; false ->
        __ReturnVal = false,        %% ILLEGAL: rebinding  
        return
    end,
    {keep_state, Data, [{reply, From, __ReturnVal}]};
```

**Fix**: Use the case expression as the value:

```erlang
active({call, From}, {is_greater, A, B}, Data) ->
    __ReturnVal = case (A > B) of
        true -> true;
        false -> false
    end,
    {keep_state, Data, [{reply, From, __ReturnVal}]};
```

Or use a fresh variable per branch. Also remove the bare `return` atom.

## Bug 2: String concatenation uses `+` instead of `++`

**Test**: ai_agent  
**Severity**: Medium

Generated code:
```erlang
Data3 = Data2#data{action_log = Data2#data.action_log + "flee,"}
```

Erlang string concatenation is `++`, not `+`:
```erlang
Data3 = Data2#data{action_log = Data2#data.action_log ++ "flee,"}
```

## Bug 3: Bare `return` atom in generated code

**Tests**: comparison_ops, equality, logical_ops, ternary_expr
**Severity**: High

The Frame `return` statement generates a bare `return` atom in Erlang, which is not a valid control flow mechanism. In gen_statem handlers, the return is the tuple `{keep_state, Data, [{reply, From, Value}]}` — the `return` statement should not emit anything, as the `__ReturnVal` mechanism already handles it.

---

## Issue 4: Frame statement expansion breaks inside native closures (4 skipped tests)

**Tests**: `while_forward_then_transition_exec`, `while_inline_forward_then_transition_exec`, `while_forward_then_native`, `while_inline_forward_stack_then_transition_exec`

These tests use native Erlang iteration (e.g., `lists:foreach`) with Frame statements inside the loop body. Erlang loops are closures (`fun`), not inline control flow like Python's `while`. The Frame statement expansion doesn't account for being inside a closure.

**What happens:**

The `.ferl` test files use native `while` syntax which is not valid Erlang. Rewriting to use `lists:foreach` reveals a deeper problem — the Erlang backend emits clause-terminating `;` instead of expression-separating `,` inside the `fun` body:

```erlang
%% Generated (broken):
a({call, From}, e, Data) ->
    lists:foreach(fun(_) ->
    p({call, From}, e, Data)     %% expanded => $^
;                                 %% BUG: ; ends the fun AND the handler clause
a({call, From}, __Event, Data) -> %% next clause, misplaced
```

**Deeper issue:**

Even with correct `,` separators, Frame statements that alter control flow (`->` transition, `=>` forward) need to return tuples from the gen_statem handler. Inside a `fun` closure, the return goes to the closure, not the handler. The transition/forward intent doesn't propagate.

**Possible solutions:**
1. **Detect and reject**: Error when Frame control-flow statements appear inside native closures
2. **Transform to recursion**: Emit a recursive helper function that threads `Data` and `From`, with Frame statements as return points
3. **Process dictionary**: Store transition intent in the process dictionary inside the closure, check after loop completes

## Issue 5: Multi-system files not supported (1 skipped test)

**Test**: `tcp_connection`

Erlang requires one module per file. Frame files with multiple `@@system` blocks generate multiple `-module()` declarations which is invalid. The backend needs to either split into separate files or generate a single module containing both systems.
