#!/usr/bin/env escript
main(_) ->
    {ok, A} = sepsisbundle:start_link(),
    "pre-recognition" = sepsisbundle:status(A),
    false = sepsisbundle:bundle_complete(A),
    sepsisbundle:lactate_drawn(A, 3.4),
    sepsisbundle:antibiotics_given(A),
    "pre-recognition" = sepsisbundle:status(A),
    sepsisbundle:recognize_sepsis(A),
    "active" = sepsisbundle:status(A),
    sepsisbundle:lactate_drawn(A, 3.4),
    sepsisbundle:cultures_drawn(A),
    tick_n(A, 15),
    sepsisbundle:antibiotics_given(A),
    sepsisbundle:fluids_complete(A),
    "active" = sepsisbundle:status(A),
    sepsisbundle:reassess_map(A, 75),
    "on time" = sepsisbundle:status(A),
    true = sepsisbundle:bundle_complete(A),
    false = sepsisbundle:pressors_indicated(A),
    case sepsisbundle:elapsed_min(A) > 60 of
        true -> io:format("FAIL: over 60~n"), halt(1);
        false -> ok
    end,
    sepsisbundle:antibiotics_given(A),
    sepsisbundle:tick_minute(A),
    "on time" = sepsisbundle:status(A),

    {ok, B} = sepsisbundle:start_link(),
    sepsisbundle:recognize_sepsis(B),
    sepsisbundle:lactate_drawn(B, 4.2),
    sepsisbundle:cultures_drawn(B),
    sepsisbundle:antibiotics_given(B),
    sepsisbundle:fluids_complete(B),
    tick_n(B, 70),
    sepsisbundle:reassess_map(B, 58),
    "active" = sepsisbundle:status(B),
    true = sepsisbundle:pressors_indicated(B),
    sepsisbundle:pressors_started(B),
    "late" = sepsisbundle:status(B),
    true = sepsisbundle:bundle_complete(B),
    case sepsisbundle:elapsed_min(B) =< 60 of
        true -> io:format("FAIL: under 60~n"), halt(1);
        false -> ok
    end,

    {ok, C} = sepsisbundle:start_link(),
    sepsisbundle:recognize_sepsis(C),
    sepsisbundle:lactate_drawn(C, 2.0),
    sepsisbundle:cultures_drawn(C),
    sepsisbundle:antibiotics_given(C),
    sepsisbundle:fluids_complete(C),
    sepsisbundle:reassess_map(C, 80),
    "on time" = sepsisbundle:status(C),

    io:format("PASS: sepsis_bundle~n"),
    halt(0).

tick_n(_S, 0) -> ok;
tick_n(S, N) ->
    sepsisbundle:tick_minute(S),
    tick_n(S, N - 1).
