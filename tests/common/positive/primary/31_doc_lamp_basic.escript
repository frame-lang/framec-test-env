#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = lamp:start_link(),
    lamp:turn_on(Pid),
    "white" = lamp:get_color(Pid),
    lamp:set_color(Pid, "blue"),
    "blue" = lamp:get_color(Pid),
    lamp:turn_off(Pid),
    io:format("PASS: 31_doc_lamp_basic~n"),
    halt(0).
