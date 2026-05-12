#!/usr/bin/env escript
%% Wave 8 parity for Erlang — int/float/bool/string round-trip.

assert_state(Label, Pid, KInt, KFloat, NInt, NFloat, NBool, NStr) ->
    case outer:get_k_int(Pid) of
        KInt -> ok;
        Got1 -> io:format("not ok 1 - persist_numeric_typing # ~s k_int: ~p~n", [Label, Got1]), halt(1)
    end,
    case outer:get_n_int(Pid) of
        NInt -> ok;
        Got2 -> io:format("not ok 1 - persist_numeric_typing # ~s n_int: ~p~n", [Label, Got2]), halt(1)
    end,
    KF = outer:get_k_float(Pid),
    case abs(KF - KFloat) < 1.0e-9 of
        true -> ok;
        false -> io:format("not ok 1 - persist_numeric_typing # ~s k_float: ~p~n", [Label, KF]), halt(1)
    end,
    NF = outer:get_n_float(Pid),
    case abs(NF - NFloat) < 1.0e-9 of
        true -> ok;
        false -> io:format("not ok 1 - persist_numeric_typing # ~s n_float: ~p~n", [Label, NF]), halt(1)
    end,
    case outer:get_n_bool(Pid) of
        NBool -> ok;
        Got5 -> io:format("not ok 1 - persist_numeric_typing # ~s n_bool: ~p~n", [Label, Got5]), halt(1)
    end,
    case outer:get_n_str(Pid) of
        NStr -> ok;
        Got6 -> io:format("not ok 1 - persist_numeric_typing # ~s n_str: ~p~n", [Label, Got6]), halt(1)
    end.

main(_) ->
    code:add_patha("."),

    O = outer:create(),
    assert_state("T0", O, 42, 1.25, 7, 2.5, true, "hello"),

    outer:bump_k_int(O),
    outer:bump_k_float(O),
    outer:bump_inner_int(O),
    outer:bump_inner_float(O),
    outer:flip_inner_bool(O),
    assert_state("T1", O, 43, 1.5, 8, 2.75, false, "hello"),

    Saved = outer:save_state(O),
    {ok, R} = outer:load_state(Saved),
    assert_state("T1 restored", R, 43, 1.5, 8, 2.75, false, "hello"),

    outer:bump_k_int(R),
    outer:bump_inner_int(R),
    assert_state("continue", R, 44, 1.5, 9, 2.75, false, "hello"),

    io:format("ok 1 - persist_numeric_typing~n"),
    init:stop().
