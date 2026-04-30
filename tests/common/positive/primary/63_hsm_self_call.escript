#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = hsm_self_call:start_link(),
    42 = hsm_self_call:drive_via_child(Pid),
    "child:before;compute@child;compute@parent;child:after;" =
        hsm_self_call:get_trace(Pid),
    io:format("PASS: 63_hsm_self_call~n"),
    halt(0).
