// @@skip — `@@fsm` removed from the validation plan (owner ruling 2026-07-30); the regex DSL is out of scope for the milestone grid.
#!/usr/bin/env escript
main(_) ->
    code:add_patha("."),
    R0 = m:recognize("ab"),
    false = maps:get(accepted, R0),
    io:format("ok 1 - 106_interior_anchor~n"),
    init:stop().
