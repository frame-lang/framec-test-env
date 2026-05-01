#!/usr/bin/env escript
%% Wave 8 parity for Erlang — 3-level nested HSM × persist.
%% Outer→Mid→Inner, each its own gen_statem process. All three
%% have HSM. Probes propagate through Pid chain; restore must
%% spawn fresh processes at every level.

probe(Pid) ->
    {outer:get_outer_state(Pid), outer:get_mid_state(Pid),
     outer:get_inner_state(Pid), outer:get_inner_count(Pid),
     outer:get_m(Pid), outer:get_k(Pid)}.

must(Label, Pid, Expected) ->
    Actual = probe(Pid),
    case Actual of
        Expected -> ok;
        _ ->
            io:format("not ok 1 - persist_three_level_nested # ~s: ~p expected ~p~n",
                      [Label, Actual, Expected]),
            halt(1)
    end.

main(_) ->
    code:add_patha("."),

    {ok, O} = outer:start_link(),
    must("T0", O, {"Idle", "P", "A", 0, 0, 0}),
    Snap0 = outer:save_state(O),
    {ok, R0} = outer:load_state(Snap0),
    must("T0 restored", R0, {"Idle", "P", "A", 0, 0, 0}),

    outer:tick(O),
    must("T1", O, {"Active", "P", "A", 0, 0, 1}),
    Snap1 = outer:save_state(O),
    {ok, R1} = outer:load_state(Snap1),
    must("T1 restored", R1, {"Active", "P", "A", 0, 0, 1}),

    outer:cycle_mid(O),
    outer:cycle_inner(O),
    must("T2", O, {"Active", "Q", "B", 1, 1, 1}),
    Snap2 = outer:save_state(O),
    {ok, R2} = outer:load_state(Snap2),
    must("T2 restored", R2, {"Active", "Q", "B", 1, 1, 1}),

    outer:cycle_inner(R2),
    must("continue1", R2, {"Active", "Q", "A", 1, 1, 1}),
    outer:cycle_mid(R2),
    must("continue2", R2, {"Active", "P", "A", 1, 1, 1}),
    outer:tick(R2),
    must("continue3", R2, {"Idle", "P", "A", 1, 1, 1}),
    outer:tick(R2),
    must("continue4", R2, {"Active", "P", "A", 1, 1, 2}),

    io:format("ok 1 - persist_three_level_nested~n"),
    init:stop().
