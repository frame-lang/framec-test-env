#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = h_s_m_enter_exit_params:start_link(),
    "Start" = h_s_m_enter_exit_params:get_state(Pid),
    h_s_m_enter_exit_params:go_to_a(Pid),
    "ChildA" = h_s_m_enter_exit_params:get_state(Pid),
    Log1 = h_s_m_enter_exit_params:get_log(Pid),
    true = (string:find(Log1, "childA_enter:starting") /= nomatch),
    h_s_m_enter_exit_params:go_to_sibling(Pid),
    "ChildB" = h_s_m_enter_exit_params:get_state(Pid),
    Log2 = h_s_m_enter_exit_params:get_log(Pid),
    true = (string:find(Log2, "childA_exit:leaving_a") /= nomatch),
    true = (string:find(Log2, "childB_enter:from_a") /= nomatch),
    io:format("PASS: 49_hsm_enter_exit_params~n"),
    halt(0).
