#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = h_s_m_enter_both:start_link(),
    Log = h_s_m_enter_both:get_log(Pid),
    io:format("Log: ~p~n", [Log]),
    %% Child enter should fire (initial state is Child)
    true = (string:find(Log, "child_enter") /= nomatch),
    io:format("PASS: 47_hsm_enter_both~n"),
    halt(0).
