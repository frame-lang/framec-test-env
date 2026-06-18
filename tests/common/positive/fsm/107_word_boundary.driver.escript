#!/usr/bin/env escript
%%! -*- erlang -*-
%% RFC-0042 @@fsm matrix sidecar: drive `recognize/1` and assert the
%% same behavior the Rust fixture's `main` asserts. The generic
%% export-walking smoke driver cannot call `recognize/1` (it would
%% pass a placeholder that crashes `list_to_tuple/1`), so this fixture
%% ships an explicit driver. A failed match aborts with a non-zero exit.
main(_) ->
    R0 = m:recognize("cat"),
    true = maps:get(accepted, R0),
    3 = maps:get(cursor, R0),
    true = maps:get(return_value, R0),
    R1 = m:recognize("cats"),
    false = maps:get(accepted, R1),
    io:format("PASS: 107_word_boundary~n"),
    halt(0).
