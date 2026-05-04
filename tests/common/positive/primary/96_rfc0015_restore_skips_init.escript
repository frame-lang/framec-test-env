#!/usr/bin/env escript
main(_) ->
    {ok, P1} = counter:start_link(),
    case counter:get_fire_count(P1) of
        1 -> ok;
        Other1 ->
            io:format("FAIL: expected 1 after construction, got ~p~n", [Other1]),
            halt(1)
    end,
    Snap = counter:snapshot(P1),

    {ok, P2} = counter:start_link(),
    case counter:get_fire_count(P2) of
        1 -> ok;
        Other2 ->
            io:format("FAIL: expected 1 on fresh construction, got ~p~n", [Other2]),
            halt(1)
    end,

    counter:rehydrate(P2, Snap),
    case counter:get_fire_count(P2) of
        1 -> ok;
        Other3 ->
            io:format("D4 violation: $> re-ran on restore (count=~p, expected 1)~n", [Other3]),
            halt(1)
    end,

    io:format("PASS: rfc0015_restore_skips_init~n"),
    halt(0).
