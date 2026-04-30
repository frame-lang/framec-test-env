#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = push_deep:start_link(),
    0 = push_deep:get_depth(Pid),
    push_deep:descend(Pid),
    1 = push_deep:get_depth(Pid),
    push_deep:descend(Pid),
    2 = push_deep:get_depth(Pid),
    push_deep:descend(Pid),
    3 = push_deep:get_depth(Pid),
    push_deep:ascend(Pid),
    2 = push_deep:get_depth(Pid),
    push_deep:ascend(Pid),
    1 = push_deep:get_depth(Pid),
    push_deep:ascend(Pid),
    0 = push_deep:get_depth(Pid),
    io:format("PASS: 70_push_depth_three~n"),
    halt(0).
