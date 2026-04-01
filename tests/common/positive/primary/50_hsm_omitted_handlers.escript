#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = h_s_m_omitted:start_link(),
    h_s_m_omitted:handled(Pid),
    "init,child_handled" = h_s_m_omitted:get_log(Pid),
    h_s_m_omitted:unhandled(Pid),
    Log = h_s_m_omitted:get_log(Pid),
    true = (string:find(Log, "parent_unhandled") /= nomatch),
    io:format("PASS: 50_hsm_omitted_handlers~n"),
    halt(0).
