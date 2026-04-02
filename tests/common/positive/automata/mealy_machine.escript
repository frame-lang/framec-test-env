#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = mealy_machine:start_link(),
    mealy_machine:i0(Pid),
    0 = mealy_machine:get_last_output(Pid),
    mealy_machine:i1(Pid),
    1 = mealy_machine:get_last_output(Pid),
    io:format("PASS: mealy_machine~n"),
    halt(0).
