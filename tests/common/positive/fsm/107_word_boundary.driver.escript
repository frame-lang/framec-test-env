// @@skip: @@fsm removed from the validation plan (owner ruling 2026-07-30); the regex DSL is out of scope for the milestone grid.
#!/usr/bin/env escript
main(_) ->
    code:add_patha("."),
    R0 = m:recognize("cat"),
    true = maps:get(accepted, R0), 3 = maps:get(cursor, R0), true = maps:get(return_value, R0),
    R1 = m:recognize("cats"),
    false = maps:get(accepted, R1),
    io:format("ok 1 - 107_word_boundary~n"),
    init:stop().
