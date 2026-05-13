#!/usr/bin/env escript
main(_) ->
    {ok, P1} = no_persist_field:start_link(),
    no_persist_field:bump(P1), no_persist_field:bump(P1), no_persist_field:bump(P1),
    no_persist_field:set_cache(P1, 99),
    no_persist_field:set_note(P1, "hello"),
    Saved = no_persist_field:save_op(P1),
    {ok, P2} = no_persist_field:load_op(Saved),
    3 = no_persist_field:get_n(P2),
    "hello" = no_persist_field:get_note(P2),
    -1 = no_persist_field:get_cache(P2),
    io:format("PASS: 100_no_persist_field~n"),
    halt(0).
