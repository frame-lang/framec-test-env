#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = s:start_link(),
    s:e(Pid),
    io:format("PASS: nested_functions~n"),
    halt(0).