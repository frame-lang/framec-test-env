#!/usr/bin/env escript
main(_) ->
    {ok, M} = stepper_driver:start_link(),
    "idle" = stepper_driver:status(M),
    0 = stepper_driver:get_position(M),

    stepper_driver:move_to(M, 300),
    "accelerating" = stepper_driver:status(M),

    {SawCruising, FinalStatus} = drive_until_idle(M, 40, false, ""),
    true = SawCruising,
    "idle" = FinalStatus,
    0 = stepper_driver:get_velocity(M),
    true = stepper_driver:get_position(M) > 200,

    {ok, M2} = stepper_driver:start_link(),
    stepper_driver:move_to(M2, 40),
    {SawCruising2, FinalStatus2} = drive_until_idle(M2, 20, false, ""),
    false = SawCruising2,
    "idle" = FinalStatus2,

    {ok, M3} = stepper_driver:start_link(),
    stepper_driver:move_to(M3, 1000),
    tick_n(M3, 15),
    "cruising" = stepper_driver:status(M3),

    stepper_driver:stop(M3),
    "decelerating" = stepper_driver:status(M3),

    tick_until_idle(M3, 15),
    "idle" = stepper_driver:status(M3),
    0 = stepper_driver:get_velocity(M3),

    {ok, M4} = stepper_driver:start_link(),
    stepper_driver:move_to(M4, 1000),
    tick_n(M4, 3),
    "accelerating" = stepper_driver:status(M4),
    stepper_driver:stall_detected(M4),
    "stalled" = stepper_driver:status(M4),
    0 = stepper_driver:get_velocity(M4),

    stepper_driver:move_to(M4, 50),
    "accelerating" = stepper_driver:status(M4),

    {ok, M5} = stepper_driver:start_link(),
    stepper_driver:stop(M5),
    stepper_driver:stall_detected(M5),
    "idle" = stepper_driver:status(M5),

    io:format("PASS: stepper_motor~n"),
    halt(0).

drive_until_idle(_M, 0, SawC, Final) -> {SawC, Final};
drive_until_idle(M, N, SawC, _Final) ->
    stepper_driver:tick(M),
    S = stepper_driver:status(M),
    NewSawC = case S of "cruising" -> true; _ -> SawC end,
    case S of
        "idle" -> {NewSawC, "idle"};
        _ -> drive_until_idle(M, N - 1, NewSawC, "")
    end.

tick_n(_M, 0) -> ok;
tick_n(M, N) ->
    stepper_driver:tick(M),
    tick_n(M, N - 1).

tick_until_idle(_M, 0) -> ok;
tick_until_idle(M, N) ->
    stepper_driver:tick(M),
    case stepper_driver:status(M) of
        "idle" -> ok;
        _ -> tick_until_idle(M, N - 1)
    end.
