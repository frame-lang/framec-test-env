#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = persist_hsm_pushpop:start_link(),
    persist_hsm_pushpop:push_modal(Pid1, 42),
    persist_hsm_pushpop:push_modal(Pid1, 99),
    99 = persist_hsm_pushpop:get_x(Pid1),
    Saved = persist_hsm_pushpop:save_state(Pid1),
    {ok, Pid2} = persist_hsm_pushpop:load_state(Saved),
    99 = persist_hsm_pushpop:get_x(Pid2),
    persist_hsm_pushpop:pop_modal(Pid2),
    42 = persist_hsm_pushpop:get_x(Pid2),
    persist_hsm_pushpop:pop_modal(Pid2),
    -99 = persist_hsm_pushpop:get_x(Pid2),
    io:format("PASS: 60_persist_hsm_pushpop~n"),
    halt(0).
