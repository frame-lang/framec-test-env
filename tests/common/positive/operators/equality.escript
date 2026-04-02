#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = equality:start_link(),
    true = equality:is_equal(Pid, 5, 5),
    false = equality:is_equal(Pid, 5, 3),
    io:format("PASS: equality~n"),
    halt(0).
