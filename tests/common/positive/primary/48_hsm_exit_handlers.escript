#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = h_s_m_exit_handlers:start_link(),
    Log1 = h_s_m_exit_handlers:get_log(Pid),
    true = (string:find(Log1, "a_enter") /= nomatch),
    h_s_m_exit_handlers:go_b(Pid),
    Log2 = h_s_m_exit_handlers:get_log(Pid),
    true = (string:find(Log2, "a_exit") /= nomatch),
    true = (string:find(Log2, "b_enter") /= nomatch),
    io:format("PASS: 48_hsm_exit_handlers~n"),
    halt(0).
