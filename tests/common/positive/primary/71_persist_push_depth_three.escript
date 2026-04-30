#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = p_push_deep:start_link(),
    p_push_deep:descend(Pid1),
    p_push_deep:descend(Pid1),
    p_push_deep:descend(Pid1),
    3 = p_push_deep:get_depth(Pid1),
    Saved = p_push_deep:save_state(Pid1),
    {ok, Pid2} = p_push_deep:load_state(Saved),
    3 = p_push_deep:get_depth(Pid2),
    p_push_deep:ascend(Pid2),
    2 = p_push_deep:get_depth(Pid2),
    p_push_deep:ascend(Pid2),
    1 = p_push_deep:get_depth(Pid2),
    p_push_deep:ascend(Pid2),
    0 = p_push_deep:get_depth(Pid2),
    io:format("PASS: 71_persist_push_depth_three~n"),
    halt(0).
