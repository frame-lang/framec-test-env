// @@skip: @@fsm removed from the validation plan (owner ruling 2026-07-30); the regex DSL is out of scope for the milestone grid.
#!/usr/bin/env escript
main(_) ->
    code:add_patha("."),
    A = m:recognize("a"),
    false = maps:get(accepted, A),
    A3 = m:recognize("aaa"),
    true = maps:get(accepted, A3), 3 = maps:get(cursor, A3), true = maps:get(return_value, A3),
    A5 = m:recognize("aaaaa"),
    true = maps:get(accepted, A5), 4 = maps:get(cursor, A5), true = maps:get(return_value, A5),
    io:format("ok 1 - 102_bounded_repetition~n"),
    init:stop().
