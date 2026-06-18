#!/usr/bin/env escript
%%! -*- erlang -*-
%% RFC-0042 @@fsm matrix sidecar: drive `recognize/1` and assert the
%% same behavior the Rust fixture's `main` asserts. The generic
%% export-walking smoke driver cannot call `recognize/1` (it would
%% pass a placeholder that crashes `list_to_tuple/1`), so this fixture
%% ships an explicit driver. A failed match aborts with a non-zero exit.
main(_) ->
    R0 = m:recognize("a"),
    false = maps:get(accepted, R0),
    R1 = m:recognize("aaa"),
    true = maps:get(accepted, R1),
    3 = maps:get(cursor, R1),
    true = maps:get(return_value, R1),
    R2 = m:recognize("aaaaa"),
    true = maps:get(accepted, R2),
    4 = maps:get(cursor, R2),
    true = maps:get(return_value, R2),
    io:format("PASS: 102_bounded_repetition~n"),
    halt(0).
