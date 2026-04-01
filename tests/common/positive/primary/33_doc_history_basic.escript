#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = history_basic:start_link(),
    "A" = history_basic:get_state(Pid),
    history_basic:goto_c_from_a(Pid),
    "C" = history_basic:get_state(Pid),
    history_basic:return_back(Pid),
    "A" = history_basic:get_state(Pid),
    history_basic:goto_b(Pid),
    "B" = history_basic:get_state(Pid),
    history_basic:goto_c_from_b(Pid),
    "C" = history_basic:get_state(Pid),
    history_basic:return_back(Pid),
    "B" = history_basic:get_state(Pid),
    io:format("PASS: 33_doc_history_basic~n"),
    halt(0).
