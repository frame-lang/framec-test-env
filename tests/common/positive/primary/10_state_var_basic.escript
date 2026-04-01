#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = state_var_basic:start_link(),
    0 = state_var_basic:get_count(Pid),
    1 = state_var_basic:increment(Pid),
    2 = state_var_basic:increment(Pid),
    3 = state_var_basic:increment(Pid),
    3 = state_var_basic:get_count(Pid),
    state_var_basic:reset(Pid),
    0 = state_var_basic:get_count(Pid),
    io:format("PASS: 10_state_var_basic~n"),
    halt(0).
