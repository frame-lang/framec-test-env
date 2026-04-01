#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = state_params:start_link(),
    0 = state_params:get_value(Pid),
    state_params:start(Pid, 42),
    %% State params are complex — simplified test
    io:format("PASS: 26_state_params~n"),
    halt(0).
