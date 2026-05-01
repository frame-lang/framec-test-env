#!/usr/bin/env escript
%% Wave 8 parity for Erlang — nested HSM × persist.
%% Outer holds Inner Pid in Data. Both have HSM ($A→$B for Inner,
%% $Idle→$Active for Outer). Three save points + continuation.

probe(Pid) ->
    {outer:get_outer_state(Pid), outer:get_inner_state(Pid),
     outer:get_inner_count(Pid), outer:get_k(Pid)}.

must(Label, Pid, Expected) ->
    Actual = probe(Pid),
    case Actual of
        Expected -> ok;
        _ ->
            io:format("not ok 1 - persist_nested_hsm # ~s: ~p expected ~p~n",
                      [Label, Actual, Expected]),
            halt(1)
    end.

main(_) ->
    code:add_patha("."),

    {ok, O} = outer:start_link(),
    must("T0 fresh", O, {"Idle", "A", 0, 0}),
    Snap0 = outer:save_state(O),
    {ok, R0} = outer:load_state(Snap0),
    must("T0 restored", R0, {"Idle", "A", 0, 0}),

    outer:tick(O),
    must("T1", O, {"Active", "A", 0, 1}),
    Snap1 = outer:save_state(O),
    {ok, R1} = outer:load_state(Snap1),
    must("T1 restored", R1, {"Active", "A", 0, 1}),

    outer:cycle_inner(O),
    must("T2", O, {"Active", "B", 1, 1}),
    Snap2 = outer:save_state(O),
    {ok, R2} = outer:load_state(Snap2),
    must("T2 restored", R2, {"Active", "B", 1, 1}),

    outer:cycle_inner(R2),
    must("continue1", R2, {"Active", "A", 1, 1}),
    outer:tick(R2),
    must("continue2", R2, {"Idle", "A", 1, 1}),
    outer:tick(R2),
    must("continue3", R2, {"Active", "A", 1, 2}),

    io:format("ok 1 - persist_nested_hsm~n"),
    init:stop().
