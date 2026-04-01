#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = interface_return:start_link(),
    true = interface_return:bool_return(Pid),
    42 = interface_return:int_return(Pid),
    "Frame" = interface_return:string_return(Pid),
    22 = interface_return:computed_return(Pid, 3, 4),
    io:format("PASS: 01_interface_return~n"),
    halt(0).
