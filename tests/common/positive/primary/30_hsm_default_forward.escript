#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = h_s_m_default_forward:start_link(),
    h_s_m_default_forward:child_only(Pid),
    h_s_m_default_forward:parent_only(Pid),
    Log = h_s_m_default_forward:get_log(Pid),
    true = (string:find(Log, "child_only") /= nomatch),
    true = (string:find(Log, "parent_only") /= nomatch),
    io:format("PASS: 30_hsm_default_forward~n"),
    halt(0).
