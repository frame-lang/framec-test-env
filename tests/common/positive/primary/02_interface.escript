#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = with_interface:start_link(),
    "Hello" = with_interface:greet(Pid, "World"),
    1 = with_interface:get_count(Pid),
    with_interface:greet(Pid, "Frame"),
    2 = with_interface:get_count(Pid),
    io:format("PASS: 02_interface~n"),
    halt(0).
