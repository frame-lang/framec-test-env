#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = context_basic:start_link(),
    20 = context_basic:set_and_get(Pid, 10),
    6 = context_basic:set_and_get(Pid, 3),
    0 = context_basic:get_default(Pid),
    io:format("PASS: 36_context_basic~n"),
    halt(0).
