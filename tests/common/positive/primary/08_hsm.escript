#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = h_s_m_forward:start_link(),
    h_s_m_forward:event_a(Pid),
    Log1 = h_s_m_forward:get_log(Pid),
    true = (string:find(Log1, "child_a") /= nomatch),
    h_s_m_forward:event_b(Pid),
    Log2 = h_s_m_forward:get_log(Pid),
    true = (string:find(Log2, "child_b_forward") /= nomatch),
    true = (string:find(Log2, "parent_b") /= nomatch),
    io:format("PASS: 08_hsm~n"),
    halt(0).
