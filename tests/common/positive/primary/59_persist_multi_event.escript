#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = persist_multi_event:start_link(),
    persist_multi_event:seed(Pid1, 42),
    42 = persist_multi_event:get_slot(Pid1),
    Saved = persist_multi_event:save_state(Pid1),
    {ok, Pid2} = persist_multi_event:load_state(Saved),
    42 = persist_multi_event:get_slot(Pid2),
    persist_multi_event:bump(Pid2),
    142 = persist_multi_event:get_slot(Pid2),
    persist_multi_event:bump(Pid2),
    242 = persist_multi_event:get_slot(Pid2),
    io:format("PASS: 59_persist_multi_event~n"),
    halt(0).
