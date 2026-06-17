#!/usr/bin/env escript
main(_) ->
    code:add_patha("."),
    R0 = m:recognize("123"),
    true = maps:get(accepted, R0), 3 = maps:get(cursor, R0), true = maps:get(return_value, R0),
    R1 = m:recognize("123x"),
    false = maps:get(accepted, R1),
    io:format("ok 1 - 105_end_anchor~n"),
    init:stop().
