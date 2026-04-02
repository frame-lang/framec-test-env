#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = arith_ops:start_link(),
    16 = arith_ops:compute(Pid, 4, 6),
    io:format("PASS: arithmetic_ops~n"),
    halt(0).
