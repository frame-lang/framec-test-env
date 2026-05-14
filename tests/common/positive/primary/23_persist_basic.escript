#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = persist_basic:start_link(),
    persist_basic:inc(Pid), persist_basic:inc(Pid), persist_basic:inc(Pid),
    3 = persist_basic:get_count(Pid),
    Saved = persist_basic:save_state(Pid),
    %% ETF wire format: binary_to_term recovers {StateAtom, PersistedMap}.
    {counting, Persisted} = binary_to_term(Saved, [safe]),
    3 = maps:get(sv_counting_count, Persisted),
    io:format("PASS: 23_persist_basic~n"),
    halt(0).
