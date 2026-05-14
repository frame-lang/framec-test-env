#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = persist_stack:start_link(),
    persist_stack:push_go(Pid1),
    "Sub" = persist_stack:get_state(Pid1),
    Saved = persist_stack:save_state(Pid1),
    %% ETF wire format: binary_to_term recovers {StateAtom, PersistedMap}.
    %% frame_stack is a list of {StateAtom, StateArgs, EnterArgs} tuples.
    {sub, Persisted} = binary_to_term(Saved, [safe]),
    [{main, _, _}] = maps:get(frame_stack, Persisted),
    {ok, Pid2} = persist_stack:load_state(Saved),
    "Sub" = persist_stack:get_state(Pid2),
    persist_stack:pop_back(Pid2),
    "Main" = persist_stack:get_state(Pid2),
    io:format("PASS: 25_persist_stack~n"),
    halt(0).
