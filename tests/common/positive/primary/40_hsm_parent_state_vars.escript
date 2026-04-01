#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = h_s_m_parent_vars:start_link(),
    h_s_m_parent_vars:child_action(Pid),
    h_s_m_parent_vars:parent_action(Pid),
    h_s_m_parent_vars:parent_action(Pid),
    2 = h_s_m_parent_vars:get_parent_count(Pid),
    Log = h_s_m_parent_vars:get_log(Pid),
    true = (string:find(Log, "child") /= nomatch),
    true = (string:find(Log, "parent") /= nomatch),
    io:format("PASS: 40_hsm_parent_state_vars~n"),
    halt(0).
