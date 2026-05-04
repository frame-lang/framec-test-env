#!/usr/bin/env escript
main(_) ->
    {ok, P1} = counter:start_link(42),
    counter:bump(P1),
    counter:bump(P1),
    case counter:get_value(P1) of
        2 -> ok;
        Other1 ->
            io:format("FAIL: via start_link expected 2, got ~p~n", [Other1]),
            halt(1)
    end,

    {ok, P2} = counter:make(99),
    counter:bump(P2),
    case counter:get_value(P2) of
        1 -> ok;
        Other2 ->
            io:format("FAIL: via make expected 1, got ~p~n", [Other2]),
            halt(1)
    end,

    io:format("PASS: rfc0015_create_rename~n"),
    halt(0).
