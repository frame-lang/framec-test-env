#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = return_init:start_link(),
    100 = return_init:get_value(Pid),
    42 = return_init:get_default(Pid),
    io:format("PASS: 35_return_init~n"),
    halt(0).
