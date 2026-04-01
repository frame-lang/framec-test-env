#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = h_s_m_enter_child:start_link(),
    Log = h_s_m_enter_child:get_log(Pid),
    true = (string:find(Log, "child_enter") /= nomatch),
    io:format("PASS: 45_hsm_enter_child_only~n"),
    halt(0).
