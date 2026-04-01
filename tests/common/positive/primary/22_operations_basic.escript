#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = ops_test:start_link(),
    110 = ops_test:compute(Pid, 10),
    105 = ops_test:compute(Pid, 5),
    io:format("PASS: 22_operations_basic~n"),
    halt(0).
