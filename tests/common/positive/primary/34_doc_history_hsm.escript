#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = history_h_s_m:start_link(),
    "Main" = history_h_s_m:get_state(Pid),
    history_h_s_m:parent_action(Pid),
    Log1 = history_h_s_m:get_log(Pid),
    true = (string:find(Log1, "parent_action") /= nomatch),
    history_h_s_m:go_sub(Pid),
    "Sub" = history_h_s_m:get_state(Pid),
    history_h_s_m:go_back(Pid),
    "Main" = history_h_s_m:get_state(Pid),
    io:format("PASS: 34_doc_history_hsm~n"),
    halt(0).
