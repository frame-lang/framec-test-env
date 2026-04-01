#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = h_s_m_multi_children:start_link(),
    Log1 = h_s_m_multi_children:get_log(Pid),
    true = (string:find(Log1, "child1_enter") /= nomatch),
    h_s_m_multi_children:parent_action(Pid),
    Log2 = h_s_m_multi_children:get_log(Pid),
    true = (string:find(Log2, "parent_action") /= nomatch),
    h_s_m_multi_children:go_child2(Pid),
    Log3 = h_s_m_multi_children:get_log(Pid),
    true = (string:find(Log3, "child2_enter") /= nomatch),
    io:format("PASS: 43_hsm_multi_children~n"),
    halt(0).
