#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = system_return:start_link(),
    42 = system_return:get_value(Pid),
    99 = system_return:get_explicit(Pid),
    io:format("PASS: 13_system_return~n"),
    halt(0).
