#!/usr/bin/env escript
main(_) ->
    code:add_patha("."),
    R0 = m:recognize("ab,cd,ef"),
    true = maps:get(accepted, R0), 3 = maps:get(cursor, R0),
    "ab," = maps:get(return_value, R0),
    io:format("ok 1 - 108_lazy_quantifier~n"),
    init:stop().
