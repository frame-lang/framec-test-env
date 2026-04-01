#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = calculator:start_link(),
    7 = calculator:add(Pid, 3, 4),
    7 = calculator:get_result(Pid),
    15 = calculator:add(Pid, 10, 5),
    io:format("PASS: 39_tagged_instantiation~n"),
    halt(0).
