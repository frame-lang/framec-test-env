#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = h_s_m_single_parent:start_link(),
    h_s_m_single_parent:child_event(Pid),
    "init,child_event" = h_s_m_single_parent:get_log(Pid),
    h_s_m_single_parent:parent_event(Pid),
    Log = h_s_m_single_parent:get_log(Pid),
    true = (string:find(Log, "parent_event") /= nomatch),
    io:format("PASS: 41_hsm_single_parent~n"),
    halt(0).
