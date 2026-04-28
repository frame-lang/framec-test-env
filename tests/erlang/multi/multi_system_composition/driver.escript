#!/usr/bin/env escript
%% Driver for tests/erlang/multi/multi_system_composition.
%%
%% The runner has compiled both logger.erl and app.erl into the
%% work_dir. The App system spins up its own Logger PID via
%% element(2, logger:start_link()) inside its #data{} record and
%% delegates log/1 calls through the cross-system call rewrite.
%% No assertion on log output — the success criterion is "no
%% crash" (the call sequence exits 0 if every state transition
%% and cross-system delegation completes).

main(_) ->
    code:add_patha("."),
    {ok, Pid} = app:start_link(),
    _ = app:start(Pid),
    _ = app:stop(Pid),
    io:format("ok 1 - multi_system_composition~n"),
    init:stop().
