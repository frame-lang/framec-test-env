#!/usr/bin/env escript
%% ============================================================================
%% Behavioral TAP driver for the maximal-coverage Erlang fixture (max_erlang).
%% Fresh machine per scenario; asserts every reachable path. Module is
%% snake_case of the system (MaxErlang -> max_erlang). Constructor: make/0
%% returns a bare Pid (runs the enter chain); save_state/1 -> blob;
%% restore_state/1 -> {ok, Pid}. Interface calls: max_erlang:evt(Pid, Args...).
%% ============================================================================
-mode(compile).

-define(N, n).

ck(Cond, Desc) ->
    K = get(?N) + 1,
    put(?N, K),
    case Cond of
        true  -> io:format("ok ~p - ~s~n", [K, Desc]);
        false -> io:format("not ok ~p - ~s~n", [K, Desc])
    end.

contains(Hay, Needle) ->
    string:find(Hay, Needle) =/= nomatch.

main(_) ->
    code:add_patha(filename:dirname(escript:script_name())),
    code:add_patha("."),
    put(?N, 0),
    io:format("TAP version 14~n"),

    %% ---- operations (instance form; bare-return passthrough) ----
    J0 = max_erlang:make(),
    ck(max_erlang:clamp(J0, 5, 99) =:= 5, "operation clamp(5,99) else-branch returns v [D]"),
    ck(max_erlang:clamp(J0, 150, 99) =:= 99, "operation clamp(150,99) if-branch returns hi [D]"),

    %% ---- HSM => $^ forward to parent ----
    A = max_erlang:make(),
    max_erlang:start(A, "J1"),
    ck(max_erlang:status(A) =:= "working", "Idle forwards status via => $^ to $Working"),
    max_erlang:submit(A, ""),
    ck(max_erlang:status(A) =:= "rejected", "submit('') terminal conditional -> $Rejected"),
    ck(contains(max_erlang:trace_of(A), "N;"), "action note() invoked from start()"),
    ck(contains(max_erlang:trace_of(A), "Boot>;"), "initial $Boot enter handler ran"),

    %% ---- state-args -> $Active(task); non-terminal mutating conditional ----
    B = max_erlang:make(),
    max_erlang:start(B, "J2"),
    max_erlang:submit(B, "payload"),
    ck(max_erlang:status(B) =:= "active", "submit(task) state-args -> $Active(task)"),
    ck(contains(max_erlang:trace_of(B), "Idle<;"), "$Idle exit handler ran on transition out"),
    ck(contains(max_erlang:trace_of(B), "Active>(payload)"), "$Active enter wrote self.pending"),
    max_erlang:tick(B),
    max_erlang:tick(B),
    max_erlang:tick(B),
    max_erlang:tick(B),
    ck(max_erlang:counter(B) =:= 3, "non-terminal if clamps attempts at max_attempts=3"),
    ck(contains(max_erlang:trace_of(B), "tick3[payload]"),
       "state-arg `task` read in regular handler + trailing read after if"),

    %% ---- exit+enter args -> $Done ----
    max_erlang:finish(B),
    ck(max_erlang:status(B) =:= "done", "finish() exit-args -> $Done"),
    ck(contains(max_erlang:trace_of(B), "Active<(done)"), "exit handler received exit arg 'done'"),
    ck(contains(max_erlang:trace_of(B), "Done>(finished)"), "enter handler received enter arg"),

    %% ---- modal push$/pop$ + depth() forwards via => $^ ----
    C = max_erlang:make(),
    max_erlang:start(C, "J3"),
    max_erlang:pause(C),
    ck(max_erlang:status(C) =:= "paused" andalso max_erlang:depth(C) =:= 1,
       "push$ -> $Paused; $Paused.$> set depth=1"),
    max_erlang:resume(C),
    ck(max_erlang:status(C) =:= "working",
       "-> pop$ restores to $Idle; depth() forwards via => $^ to $Working"),
    ck(max_erlang:depth(C) =:= 0,
       "-> pop$ fires $Paused.<$ exit handler; stack_depth back to 0 [G]"),

    %% ---- nested modal stack (two push$, two pop$) ----
    CN = max_erlang:make(),
    max_erlang:start(CN, "J3b"),
    max_erlang:pause(CN),
    max_erlang:pause(CN),
    ck(max_erlang:status(CN) =:= "paused", "nested push$ twice -> still $Paused"),
    max_erlang:resume(CN),
    max_erlang:resume(CN),
    ck(max_erlang:status(CN) =:= "working", "two -> pop$ restore through the stack to $Idle"),
    ck(max_erlang:depth(CN) =:= 0, "both pops fired $Paused.<$; stack_depth back to 0 [G]"),

    %% ---- iteration via driver-pumped self-transition (NO native while) ----
    D = max_erlang:make(),
    max_erlang:start(D, "spin"),
    ck(max_erlang:status(D) =:= "spinning", "start('spin') -> $Spinning"),
    pump_until_idle(D, 10),
    ck(max_erlang:spin_done(D) =:= 5, "self-transition loop pumped spins to spin_target=5"),
    ck(max_erlang:status(D) =:= "working", "loop exit transitioned $Spinning -> $Idle (=> $Working)"),

    %% ---- persist round-trip incl. state-arg survival + @@[no_persist] reset ----
    E = max_erlang:make(),
    max_erlang:start(E, "J5"),
    max_erlang:submit(E, "z"),
    max_erlang:tick(E),
    Snap = max_erlang:save_state(E),
    {ok, E2} = max_erlang:restore_state(Snap),
    ck(max_erlang:trace_of(E2) =:= max_erlang:trace_of(E)
       andalso contains(max_erlang:trace_of(E2), "Active>(z)"),
       "persist restores FULL trace incl. state-arg 'z' (deep equality)"),
    ck(max_erlang:counter(E2) =:= max_erlang:counter(E)
       andalso max_erlang:status(E2) =:= "active",
       "persist restores domain + current state"),
    ck(max_erlang:scratch_of(E) =:= 1 andalso max_erlang:scratch_of(E2) =:= 0,
       "@@[no_persist] scratch excluded from blob (restore resets to default 0)"),

    %% ---- construct probe subgraph ($A/$B/$C via start('probe')) ----
    PR = max_erlang:make(),
    max_erlang:start(PR, "probe"),
    ck(max_erlang:here(PR) =:= "A", "@@:system.state.name reports $A"),
    ck(max_erlang:echo(PR, "hi") =:= "echo:hi", "@@:data.k set+read (call-scoped) + @@:params.x [E]"),
    ck(max_erlang:cap(PR) =:= 50, "uppercase const read self.LIMIT = 50 [B]"),
    ck(max_erlang:classify(PR, -1) =:= "neg", "elif ladder: n<0 -> neg"),
    ck(max_erlang:classify(PR, 0) =:= "zero", "elif ladder: n==0 -> zero"),
    ck(max_erlang:classify(PR, 50) =:= "pos", "elif ladder: nested else -> pos"),
    ck(max_erlang:classify(PR, 200) =:= "big", "elif ladder: nested if -> big"),
    ck(max_erlang:guard(PR) =:= 50, "@@:return(e) returns the value"),
    ck(not contains(max_erlang:trace_of(PR), "LEAK"),
       "@@:return(e) short-circuits: trailing note(LEAK) did not run [F]"),

    %% @@:event + labeled transition -> $B  (@@:event is an ATOM in Erlang)
    PRf = max_erlang:make(),
    max_erlang:start(PRf, "probe"),
    max_erlang:fire(PRf),
    ck(max_erlang:here(PRf) =:= "B", "labeled transition -> $B"),
    ck(max_erlang:evt(PRf) =:= fire, "@@:event recorded the firing event name (atom)"),

    %% forward transition -> => $B re-dispatches relay
    PRr = max_erlang:make(),
    max_erlang:start(PRr, "probe"),
    max_erlang:relay(PRr),
    ck(max_erlang:here(PRr) =:= "B" andalso contains(max_erlang:trace_of(PRr), "B.relay;"),
       "forward transition -> => $B re-dispatched relay to $B"),

    %% action invocation + reentrant @@:self.fire()
    PRp = max_erlang:make(),
    max_erlang:start(PRp, "probe"),
    max_erlang:ping(PRp),
    ck(contains(max_erlang:trace_of(PRp), "ping;") andalso max_erlang:here(PRp) =:= "B",
       "action invocation + reentrant @@:self.fire() landed in $B"),

    %% decorated forward transition WITH state args -> => $C("payload") (#128)
    PRw = max_erlang:make(),
    max_erlang:start(PRw, "probe"),
    max_erlang:fwd(PRw),
    ck(max_erlang:here(PRw) =:= "C" andalso contains(max_erlang:trace_of(PRw), "C.fwd(payload)"),
       "forward transition WITH state args -> => $C(arg) [#128]"),

    io:format("1..~p~n", [get(?N)]),
    halt(0).

%% drive pump() until the machine leaves $Spinning (guarded; max attempts)
pump_until_idle(_Pid, 0) -> ok;
pump_until_idle(Pid, Fuel) ->
    case max_erlang:status(Pid) of
        "spinning" ->
            max_erlang:pump(Pid),
            pump_until_idle(Pid, Fuel - 1);
        _ -> ok
    end.
