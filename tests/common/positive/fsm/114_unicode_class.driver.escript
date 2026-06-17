#!/usr/bin/env escript
main(_) ->
    code:add_patha("."),
    R0 = m:recognize("abc"),
    true = maps:get(accepted, R0), 3 = maps:get(cursor, R0), true = maps:get(return_value, R0),
    R1 = m:recognize("1a"),
    false = maps:get(accepted, R1),
    io:format("ok 1 - 114_unicode_class~n"),
    init:stop().
