#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = native_code:start_link(),
    20 = native_code:compute(Pid, 10),
    15 = native_code:compute(Pid, 5),
    io:format("PASS: 04_native_code~n"),
    halt(0).
