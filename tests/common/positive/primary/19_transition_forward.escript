#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = transition_forward:start_link(),
    "Main" = transition_forward:get_state(Pid),
    transition_forward:go_to_child(Pid),
    "Child" = transition_forward:get_state(Pid),
    io:format("PASS: 19_transition_forward~n"),
    halt(0).
