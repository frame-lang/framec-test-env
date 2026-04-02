#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = logical_ops:start_link(),
    true = logical_ops:check(Pid, true, true),
    false = logical_ops:check(Pid, true, false),
    io:format("PASS: logical_ops~n"),
    halt(0).
