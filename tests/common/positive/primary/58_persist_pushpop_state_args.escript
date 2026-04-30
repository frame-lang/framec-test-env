#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = persist_pushpop_state_args:start_link(),
    persist_pushpop_state_args:push_modal(Pid1, 42),
    persist_pushpop_state_args:push_modal(Pid1, 77),
    77 = persist_pushpop_state_args:get_slot(Pid1),
    Saved = persist_pushpop_state_args:save_state(Pid1),
    {ok, Pid2} = persist_pushpop_state_args:load_state(Saved),
    77 = persist_pushpop_state_args:get_slot(Pid2),
    persist_pushpop_state_args:pop_modal(Pid2),
    42 = persist_pushpop_state_args:get_slot(Pid2),
    persist_pushpop_state_args:pop_modal(Pid2),
    -99 = persist_pushpop_state_args:get_slot(Pid2),
    io:format("PASS: 58_persist_pushpop_state_args~n"),
    halt(0).
