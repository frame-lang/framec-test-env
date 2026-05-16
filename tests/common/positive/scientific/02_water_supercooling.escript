#!/usr/bin/env escript
main(_) ->
    {ok, W} = water:start_link(),
    "liquid" = water:phase(W),
    water:cool(W, 30.0),
    "supercooled liquid" = water:phase(W),
    water:shake(W),
    "ice" = water:phase(W),

    {ok, W2} = water:start_link(),
    water:cool(W2, 30.0),
    "supercooled liquid" = water:phase(W2),
    case water:temperature(W) == water:temperature(W2) of
        true -> ok;
        false -> io:format("FAIL: same temp~n"), halt(1)
    end,
    case water:phase(W) == water:phase(W2) of
        true -> io:format("FAIL: phases should differ~n"), halt(1);
        false -> ok
    end,

    {ok, W3} = water:start_link(),
    water:cool(W3, 30.0),
    water:nucleate(W3),
    "ice" = water:phase(W3),

    {ok, W4} = water:start_link(),
    water:cool(W4, 30.0),
    "supercooled liquid" = water:phase(W4),
    water:cool(W4, 40.0),
    "ice" = water:phase(W4),
    water:heat(W4, 50.0),
    "liquid" = water:phase(W4),

    {ok, W5} = water:start_link(),
    water:shake(W5),
    "liquid" = water:phase(W5),
    {ok, W6} = water:start_link(),
    water:cool(W6, 30.0),
    water:cool(W6, 40.0),
    "ice" = water:phase(W6),
    water:shake(W6),
    "ice" = water:phase(W6),

    io:format("PASS: water_supercooling~n"),
    halt(0).
