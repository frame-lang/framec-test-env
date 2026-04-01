#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = h_s_m_siblings:start_link(),
    "A" = h_s_m_siblings:get_state(Pid),
    h_s_m_siblings:go_b(Pid),
    "B" = h_s_m_siblings:get_state(Pid),
    h_s_m_siblings:go_a(Pid),
    "A" = h_s_m_siblings:get_state(Pid),
    io:format("PASS: 44_hsm_sibling_transitions~n"),
    halt(0).
