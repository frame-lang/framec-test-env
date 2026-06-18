#!/usr/bin/env escript
%%! -*- erlang -*-
%% RFC-0042 @@fsm matrix sidecar: drive `recognize/1` and assert the
%% same behavior the Rust fixture's `main` asserts. The generic
%% export-walking smoke driver cannot call `recognize/1` (it would
%% pass a placeholder that crashes `list_to_tuple/1`), so this fixture
%% ships an explicit driver. A failed match aborts with a non-zero exit.
main(_) ->
    R0 = digits:recognize("123"),
    true = maps:get(accepted, R0),
    3 = maps:get(cursor, R0),
    true = maps:get(return_value, R0),
    R1 = digits:recognize("xyz"),
    false = maps:get(accepted, R1),
    io:format("PASS: 100_match_digits~n"),
    halt(0).
