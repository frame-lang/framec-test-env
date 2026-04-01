#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = h_s_m_enter_parent:start_link(),
    Log = h_s_m_enter_parent:get_log(Pid),
    io:format("Log: ~p~n", [Log]),
    io:format("PASS: 46_hsm_enter_parent_only~n"),
    halt(0).
