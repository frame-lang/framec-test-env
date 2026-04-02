#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = interface_param:start_link(),
    "hello" = interface_param:greet(Pid, "world"),
    io:format("PASS: interface_with_param~n"),
    halt(0).
