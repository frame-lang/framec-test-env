#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = s:start_link(),
    s:e(Pid),
    io:format("PASS: function_scope~n"),
    halt(0).