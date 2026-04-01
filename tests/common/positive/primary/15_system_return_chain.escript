#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = return_chain:start_link(),
    1 = return_chain:get_value(Pid),
    return_chain:go_next(Pid),
    2 = return_chain:get_value(Pid),
    return_chain:go_next(Pid),
    3 = return_chain:get_value(Pid),
    return_chain:go_next(Pid),
    1 = return_chain:get_value(Pid),
    io:format("PASS: 15_system_return_chain~n"),
    halt(0).
