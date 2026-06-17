#!/usr/bin/env escript
main(_) ->
    code:add_patha("."),
    Cat = m:recognize("cat"),
    true = maps:get(accepted, Cat), 3 = maps:get(cursor, Cat), true = maps:get(return_value, Cat),
    Dog = m:recognize("dog"),
    true = maps:get(accepted, Dog), 3 = maps:get(cursor, Dog), true = maps:get(return_value, Dog),
    Cow = m:recognize("cow"),
    false = maps:get(accepted, Cow),
    io:format("ok 1 - 101_alternation~n"),
    init:stop().
