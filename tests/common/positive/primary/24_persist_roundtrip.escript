#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = persist_roundtrip:start_link(),
    persist_roundtrip:go_active(Pid1),
    "active" = persist_roundtrip:get_state(Pid1),
    persist_roundtrip:set_counter(Pid1, 42),
    42 = persist_roundtrip:get_counter(Pid1),
    Saved = persist_roundtrip:save_state(Pid1),
    active = maps:get(state, Saved),
    42 = maps:get(counter, Saved),
    {ok, Pid2} = persist_roundtrip:load_state(Saved),
    "active" = persist_roundtrip:get_state(Pid2),
    42 = persist_roundtrip:get_counter(Pid2),
    persist_roundtrip:go_idle(Pid2),
    "idle" = persist_roundtrip:get_state(Pid2),
    io:format("PASS: 24_persist_roundtrip~n"),
    halt(0).
