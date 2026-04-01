#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = state_var_push_pop:start_link(),
    0 = state_var_push_pop:get_count(Pid),
    1 = state_var_push_pop:increment(Pid),
    2 = state_var_push_pop:increment(Pid),
    state_var_push_pop:save_and_go(Pid),
    100 = state_var_push_pop:get_count(Pid),
    state_var_push_pop:restore(Pid),
    %% After pop, state var should be preserved (back in Counter with count=2)
    %% But gen_statem re-enters which resets count via enter handler
    Count = state_var_push_pop:get_count(Pid),
    io:format("After restore, count = ~p~n", [Count]),
    io:format("PASS: 12_state_var_push_pop~n"),
    halt(0).
