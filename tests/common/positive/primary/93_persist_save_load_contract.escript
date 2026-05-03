#!/usr/bin/env escript
main(_) ->
    {ok, P1} = counter:start_link(),
    counter:bump(P1), counter:bump(P1), counter:bump(P1),
    Saved = counter:save_op(P1),
    {ok, P2} = counter:load_op(Saved),
    3 = counter:get_n(P2),
    io:format("PASS: 93_persist_save_load_contract~n"),
    halt(0).
