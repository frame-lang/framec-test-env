#!/usr/bin/env escript
main(_) ->
    Pid1 = persist_list:create(),
    persist_list:configure(Pid1, [10, 20, 30]),
    10 = persist_list:first_item(Pid1),
    Saved = persist_list:save_state(Pid1),
    {ok, Pid2} = persist_list:load_state(Saved),
    10 = persist_list:first_item(Pid2),
    3 = persist_list:size(Pid2),
    io:format("PASS: 74_persist_list_state_arg~n"),
    halt(0).
