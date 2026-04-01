#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = state_var_reentry:start_link(),
    0 = state_var_reentry:get_count(Pid),
    1 = state_var_reentry:increment(Pid),
    2 = state_var_reentry:increment(Pid),
    state_var_reentry:go_other(Pid),
    -1 = state_var_reentry:get_count(Pid),
    state_var_reentry:come_back(Pid),
    %% State var resets on re-entry
    0 = state_var_reentry:get_count(Pid),
    io:format("PASS: 11_state_var_reentry~n"),
    halt(0).
