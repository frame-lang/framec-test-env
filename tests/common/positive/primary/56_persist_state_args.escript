#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = persist_state_args:start_link(),
    persist_state_args:kick(Pid1, 42),
    42 = persist_state_args:get_slot(Pid1),
    Saved = persist_state_args:save_state(Pid1),
    {ok, Pid2} = persist_state_args:load_state(Saved),
    42 = persist_state_args:get_slot(Pid2),
    persist_state_args:kick(Pid2, 99),
    99 = persist_state_args:get_slot(Pid2),
    io:format("PASS: 56_persist_state_args~n"),
    halt(0).
