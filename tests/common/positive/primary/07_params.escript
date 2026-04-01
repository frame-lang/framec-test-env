#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = with_params:start_link(),
    0 = with_params:get_total(Pid),
    with_params:start(Pid, 10),
    10 = with_params:get_total(Pid),
    with_params:add(Pid, 5),
    15 = with_params:get_total(Pid),
    6 = with_params:multiply(Pid, 2, 3),
    21 = with_params:get_total(Pid),
    io:format("PASS: 07_params~n"),
    halt(0).
