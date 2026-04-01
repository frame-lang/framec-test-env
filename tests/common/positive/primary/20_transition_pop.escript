#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = transition_pop:start_link(),
    "Idle" = transition_pop:get_state(Pid),
    transition_pop:start(Pid),
    "Working" = transition_pop:get_state(Pid),
    transition_pop:process(Pid),
    "Idle" = transition_pop:get_state(Pid),
    io:format("PASS: 20_transition_pop~n"),
    halt(0).
