#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = moore_machine:start_link(),
    0 = moore_machine:get_output(Pid),
    moore_machine:i0(Pid),
    1 = moore_machine:get_output(Pid),
    moore_machine:i1(Pid),
    2 = moore_machine:get_output(Pid),
    moore_machine:i0(Pid),
    0 = moore_machine:get_output(Pid),
    io:format("PASS: moore_machine~n"),
    halt(0).
