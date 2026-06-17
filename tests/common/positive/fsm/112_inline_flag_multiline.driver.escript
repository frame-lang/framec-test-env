#!/usr/bin/env escript
main(_) ->
    code:add_patha("."),
    R0 = m:recognize("a\nb"),
    true = maps:get(accepted, R0), 1 = maps:get(cursor, R0), true = maps:get(return_value, R0),
    R1 = m:recognize("ab"),
    false = maps:get(accepted, R1),
    io:format("ok 1 - 112_inline_flag_multiline~n"),
    init:stop().
