#!/usr/bin/env escript
main(_) ->
    {ok, P} = peg_insertion:start_link(),
    "idle" = peg_insertion:status(P),

    peg_insertion:start(P, 10.0),
    "approaching" = peg_insertion:status(P),

    peg_insertion:force_reading(P, 2.0),
    "searching" = peg_insertion:status(P),

    peg_insertion:force_reading(P, 0.05),
    "inserting" = peg_insertion:status(P),

    seat_loop(P, 0),
    "seated" = peg_insertion:status(P),

    {ok, P2} = peg_insertion:start_link(),
    peg_insertion:start(P2, 10.0),
    peg_insertion:force_reading(P2, 2.0),
    peg_insertion:force_reading(P2, 0.05),
    peg_insertion:force_reading(P2, 15.0),
    "jammed" = peg_insertion:status(P2),
    1 = peg_insertion:get_retries(P2),

    peg_insertion:tick(P2),
    "retreating" = peg_insertion:status(P2),
    peg_insertion:tick(P2),
    "searching" = peg_insertion:status(P2),

    peg_insertion:force_reading(P2, 0.05),
    "inserting" = peg_insertion:status(P2),
    peg_insertion:force_reading(P2, 15.0),
    "jammed" = peg_insertion:status(P2),
    peg_insertion:tick(P2),
    "failed" = peg_insertion:status(P2),

    {ok, P3} = peg_insertion:start_link(),
    peg_insertion:start(P3, 10.0),
    peg_insertion:force_reading(P3, 2.0),
    search_timeout_loop(P3, 0),
    "retreating" = peg_insertion:status(P3),

    {ok, P4} = peg_insertion:start_link(),
    peg_insertion:start(P4, 10.0),
    peg_insertion:force_reading(P4, 2.0),
    peg_insertion:force_reading(P4, 0.05),
    peg_insertion:abort(P4),
    "retracting" = peg_insertion:status(P4),
    peg_insertion:retracted(P4),
    "idle" = peg_insertion:status(P4),

    io:format("PASS: peg_insertion~n"),
    halt(0).

seat_loop(_P, 220) -> ok;
seat_loop(P, I) ->
    peg_insertion:tick(P),
    case peg_insertion:status(P) of
        "seated" -> ok;
        _ -> seat_loop(P, I + 1)
    end.

search_timeout_loop(_P, 35) -> ok;
search_timeout_loop(P, I) ->
    peg_insertion:tick(P),
    case peg_insertion:status(P) of
        "searching" -> search_timeout_loop(P, I + 1);
        _ -> ok
    end.
