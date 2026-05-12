#!/usr/bin/env escript
%% Wave 8 parity for Erlang — multi-instance independence under
%% nested persist. Two Outer trajectories restored in reversed
%% order; mutating one must not affect the other.

probe(Pid) ->
    {outer:get_outer_state(Pid), outer:get_inner_state(Pid),
     outer:get_inner_count(Pid), outer:get_k(Pid)}.

must(Label, Pid, Expected) ->
    Actual = probe(Pid),
    case Actual of
        Expected -> ok;
        _ ->
            io:format("not ok 1 - persist_multi_instance # ~s: ~p expected ~p~n",
                      [Label, Actual, Expected]),
            halt(1)
    end.

main(_) ->
    code:add_patha("."),

    O1 = outer:create(),
    O2 = outer:create(),

    outer:cycle_inner(O1),
    outer:cycle_inner(O1),
    outer:cycle_inner(O1),
    must("o1 pre", O1, {"Idle", "B", 2, 0}),

    outer:tick(O2),
    outer:tick(O2),
    outer:tick(O2),
    must("o2 pre", O2, {"Active", "A", 0, 2}),

    Snap1 = outer:save_state(O1),
    Snap2 = outer:save_state(O2),

    {ok, R2} = outer:load_state(Snap2),
    {ok, R1} = outer:load_state(Snap1),

    must("r1 restored", R1, {"Idle", "B", 2, 0}),
    must("r2 restored", R2, {"Active", "A", 0, 2}),

    outer:cycle_inner(R1),
    must("r1 after mut", R1, {"Idle", "A", 2, 0}),
    must("r2 after r1 mut", R2, {"Active", "A", 0, 2}),

    outer:cycle_inner(R2),
    must("r1 after r2 mut", R1, {"Idle", "A", 2, 0}),
    must("r2 after r2 mut", R2, {"Active", "B", 1, 2}),

    io:format("ok 1 - persist_multi_instance~n"),
    init:stop().
