// @@skip — `@@fsm` removed from the validation plan (owner ruling 2026-07-30); the regex DSL is out of scope for the milestone grid.
#!/usr/bin/env escript
%% Behavioral driver for FSM-MATRIX 100 (Erlang). Mirrors the Python/Rust
%% contract: `digits:recognize/1` returns the final recognizer-state map.
main(_) ->
    code:add_patha("."),
    Ok = digits:recognize("123"),
    true = maps:get(accepted, Ok),
    3 = maps:get(cursor, Ok),
    true = maps:get(return_value, Ok),
    Bad = digits:recognize("xyz"),
    false = maps:get(accepted, Bad),
    io:format("ok 1 - 100_match_digits~n"),
    init:stop().
