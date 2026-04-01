#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = persist_stack:start_link(),
    persist_stack:push_go(Pid1),
    "Sub" = persist_stack:get_state(Pid1),
    Saved = persist_stack:save_state(Pid1),
    sub = maps:get(state, Saved),
    [main] = maps:get(frame_stack, Saved),
    {ok, Pid2} = persist_stack:load_state(Saved),
    "Sub" = persist_stack:get_state(Pid2),
    persist_stack:pop_back(Pid2),
    "Main" = persist_stack:get_state(Pid2),
    io:format("PASS: 25_persist_stack~n"),
    halt(0).
