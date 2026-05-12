#!/usr/bin/env escript
%% Driver for tests/erlang/multi/ai_agent.
%%
%% Tests cross-system embedding (Agent → ToolRunner) plus a
%% multi-stage state machine that walks Idle → Planning →
%% AwaitingApproval → Coding (×2 step calls) → Testing → Complete.

main(_) ->
    code:add_patha("."),
    Pid = agent:create(),

    %% Initial: idle.
    "idle" = agent:status(Pid),

    %% task/1 transitions to $Planning. Enter sets plan_len = 2.
    _ = agent:task(Pid, "Add validation"),
    "planning" = agent:status(Pid),

    %% step/0 → $AwaitingApproval.
    _ = agent:step(Pid),
    "awaiting_approval" = agent:status(Pid),

    %% approve/0 → $Coding (step_idx = 0, no work in enter).
    _ = agent:approve(Pid),
    "coding" = agent:status(Pid),

    %% step/0 → executes "read_file", step_idx 0→1, stays in $Coding.
    _ = agent:step(Pid),
    "coding" = agent:status(Pid),

    %% step/0 → executes "write_file", step_idx 1→2, transitions
    %% to $Testing. Enter calls tool_runner.execute("run_terminal")
    %% which returns "tests passed".
    _ = agent:step(Pid),
    "testing" = agent:status(Pid),

    %% step/0 → $Complete.
    _ = agent:step(Pid),
    "complete" = agent:status(Pid),

    io:format("ok 1 - ai_agent~n"),
    init:stop().
