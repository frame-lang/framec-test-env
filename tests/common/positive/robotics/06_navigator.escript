#!/usr/bin/env escript
main(_) ->
    {ok, N} = navigator:start_link(),
    "idle" = navigator:status(N),

    navigator:navigate_to(N, 5.0, 0.0),
    "planning" = navigator:status(N),

    navigator:plan_ready(N, 3),
    "driving" = navigator:status(N),

    navigator:tick(N, 10.0, 0),
    "driving" = navigator:status(N),
    navigator:tick(N, 10.0, 0),
    "driving" = navigator:status(N),

    navigator:tick(N, 10.0, 1),
    "arrived" = navigator:status(N),

    {ok, N2} = navigator:start_link(),
    navigator:navigate_to(N2, 5.0, 0.0),
    navigator:plan_failed(N2),
    "planning" = navigator:status(N2),
    1 = navigator:get_replans(N2),
    navigator:plan_failed(N2),
    2 = navigator:get_replans(N2),
    navigator:plan_failed(N2),
    "failed" = navigator:status(N2),

    {ok, N3} = navigator:start_link(),
    navigator:navigate_to(N3, 5.0, 0.0),
    navigator:plan_ready(N3, 0),
    "planning" = navigator:status(N3),
    1 = navigator:get_replans(N3),

    {ok, N4} = navigator:start_link(),
    navigator:navigate_to(N4, 5.0, 0.0),
    navigator:plan_ready(N4, 5),
    navigator:tick(N4, 10.0, 0),
    navigator:tick(N4, 0.3, 0),
    "avoiding" = navigator:status(N4),

    navigator:tick(N4, 10.0, 0),
    "planning" = navigator:status(N4),

    {ok, N5} = navigator:start_link(),
    navigator:navigate_to(N5, 5.0, 0.0),
    navigator:plan_ready(N5, 5),
    navigator:tick(N5, 0.3, 0),
    "avoiding" = navigator:status(N5),
    tick_until_failed(N5, 35),
    "failed" = navigator:status(N5),

    {ok, N6} = navigator:start_link(),
    navigator:navigate_to(N6, 5.0, 0.0),
    navigator:plan_ready(N6, 2),
    navigator:tick(N6, 10.0, 0),
    navigator:tick(N6, 10.0, 0),
    "planning" = navigator:status(N6),

    {ok, N7} = navigator:start_link(),
    navigator:navigate_to(N7, 5.0, 0.0),
    navigator:plan_ready(N7, 3),
    navigator:abort(N7),
    "idle" = navigator:status(N7),

    {ok, N8} = navigator:start_link(),
    navigator:navigate_to(N8, 5.0, 0.0),
    navigator:plan_ready(N8, 5),
    navigator:tick(N8, 0.3, 0),
    navigator:abort(N8),
    "idle" = navigator:status(N8),

    navigator:navigate_to(N2, 10.0, 0.0),
    "planning" = navigator:status(N2),
    0 = navigator:get_replans(N2),

    io:format("PASS: navigator~n"),
    halt(0).

tick_until_failed(_S, 0) -> ok;
tick_until_failed(S, N) ->
    navigator:tick(S, 0.3, 0),
    case navigator:status(S) of
        "failed" -> ok;
        _ -> tick_until_failed(S, N - 1)
    end.
