// @@skip — `@@fsm` removed from the validation plan (owner ruling 2026-07-30); the regex DSL is out of scope for the milestone grid.
#!/usr/bin/env escript
%% Token alphabet: token kinds are atoms (recognize/1 over a list of atoms).
main(_) ->
    code:add_patha("."),
    Ok = m:recognize(['IDENT', 'LPAREN']),
    true = maps:get(accepted, Ok), 2 = maps:get(cursor, Ok), true = maps:get(return_value, Ok),
    Bad = m:recognize(['IDENT', 'IDENT']),
    false = maps:get(accepted, Bad),
    io:format("ok 1 - 117_token_alphabet~n"),
    init:stop().
