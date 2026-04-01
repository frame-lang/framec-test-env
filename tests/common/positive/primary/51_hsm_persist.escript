#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = h_s_m_persist:start_link(),
    h_s_m_persist:child_action(Pid1),
    h_s_m_persist:parent_action(Pid1),
    Log1 = h_s_m_persist:get_log(Pid1),
    true = (string:find(Log1, "child") /= nomatch),
    true = (string:find(Log1, "parent") /= nomatch),
    Saved = h_s_m_persist:save_state(Pid1),
    {ok, Pid2} = h_s_m_persist:load_state(Saved),
    Log2 = h_s_m_persist:get_log(Pid2),
    Log1 = Log2,
    io:format("PASS: 51_hsm_persist~n"),
    halt(0).
