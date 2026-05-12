#!/usr/bin/env escript
%% Driver for tests/erlang/multi/counter_pair.
%%
%% The runner has compiled both counter.erl and driver_sys.erl into
%% the work_dir. We exercise cross-system PID wiring: bump_inner/1 on
%% the Driver should delegate to the embedded Counter (which lives in
%% a separate gen_statem PID), then inner_count/1 should reflect the
%% bumps.

main(_) ->
    code:add_patha("."),

    %% Driver_sys spins up its own Counter inside its #data{} record.
    Pid = driver_sys:create(),

    %% Three bumps go through the cross-system call rewrite:
    %%   self.counter.bump()  →  counter:bump(Data#data.counter)
    _ = driver_sys:bump_inner(Pid),
    _ = driver_sys:bump_inner(Pid),
    _ = driver_sys:bump_inner(Pid),

    %% Read back the embedded counter's value via the same path.
    Count = driver_sys:inner_count(Pid),
    case Count of
        3 -> io:format("ok 1 - counter_pair~n"), init:stop();
        Other ->
            io:format("not ok 1 - counter_pair # expected 3, got ~p~n", [Other]),
            halt(1)
    end.
