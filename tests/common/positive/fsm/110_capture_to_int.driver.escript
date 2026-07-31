// @@skip — `@@fsm` removed from the validation plan (owner ruling 2026-07-30); the regex DSL is out of scope for the milestone grid.
#!/usr/bin/env escript
main(_) ->
    code:add_patha("."),
    R0 = m:recognize("42"),
    true = maps:get(accepted, R0), 2 = maps:get(cursor, R0), 42 = maps:get(return_value, R0),
    R1 = m:recognize("x"),
    false = maps:get(accepted, R1),
    io:format("ok 1 - 110_capture_to_int~n"),
    init:stop().
