// @@skip: @@fsm removed from the validation plan (owner ruling 2026-07-30); the regex DSL is out of scope for the milestone grid.
#!/usr/bin/env escript
main(_) ->
    code:add_patha("."),
    R0 = m:recognize("aaab"),
    true = maps:get(accepted, R0), 4 = maps:get(cursor, R0), true = maps:get(return_value, R0),
    R1 = m:recognize("b"),
    true = maps:get(accepted, R1), 1 = maps:get(cursor, R1), true = maps:get(return_value, R1),
    R2 = m:recognize("aaa"),
    false = maps:get(accepted, R2),
    io:format("ok 1 - 103_greedy_longest~n"),
    init:stop().
