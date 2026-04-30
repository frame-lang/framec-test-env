#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = persist_hsm_state_args:start_link(),
    persist_hsm_state_args:drive(Pid1, 42),
    42 = persist_hsm_state_args:get_x(Pid1),
    Saved = persist_hsm_state_args:save_state(Pid1),
    {ok, Pid2} = persist_hsm_state_args:load_state(Saved),
    42 = persist_hsm_state_args:get_x(Pid2),
    persist_hsm_state_args:drive(Pid2, 99),
    99 = persist_hsm_state_args:get_x(Pid2),
    io:format("PASS: 57_persist_hsm_state_args~n"),
    halt(0).
