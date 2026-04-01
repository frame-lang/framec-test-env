#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = return_reentrant:start_link(),
    "outer" = return_reentrant:outer_call(Pid),
    "inner" = return_reentrant:inner_call(Pid),
    io:format("PASS: 16_system_return_reentrant~n"),
    halt(0).
