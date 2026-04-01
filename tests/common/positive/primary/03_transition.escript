#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = with_transition:start_link(),

    "First" = with_transition:get_state(Pid),
    with_transition:next(Pid),
    "Second" = with_transition:get_state(Pid),
    with_transition:next(Pid),
    "First" = with_transition:get_state(Pid),

    io:format("PASS: 03_transition~n"),
    halt(0).
