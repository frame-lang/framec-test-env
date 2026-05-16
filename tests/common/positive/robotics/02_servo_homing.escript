#!/usr/bin/env escript
main(_) ->
    {ok, S} = servo_homing:start_link(),
    "unhomed" = servo_homing:status(S),

    servo_homing:home(S),
    "seeking limit" = servo_homing:status(S),
    1 = servo_homing:get_attempts(S),

    tick_n(S, 3),
    servo_homing:limit_hit(S),
    "backing off" = servo_homing:status(S),

    servo_homing:tick(S),
    servo_homing:tick(S),
    "finding index" = servo_homing:status(S),

    servo_homing:index_pulse(S),
    "homed" = servo_homing:status(S),

    servo_homing:home(S),
    "seeking limit" = servo_homing:status(S),
    1 = servo_homing:get_attempts(S),

    {ok, S2} = servo_homing:start_link(),
    servo_homing:home(S2),
    tick_n(S2, 21),
    "seeking limit" = servo_homing:status(S2),
    2 = servo_homing:get_attempts(S2),

    tick_n(S2, 21),
    3 = servo_homing:get_attempts(S2),

    tick_n(S2, 21),
    "fault" = servo_homing:status(S2),

    servo_homing:home(S2),
    "seeking limit" = servo_homing:status(S2),
    1 = servo_homing:get_attempts(S2),

    {ok, S3} = servo_homing:start_link(),
    servo_homing:home(S3),
    servo_homing:limit_hit(S3),
    servo_homing:tick(S3), servo_homing:tick(S3),
    "finding index" = servo_homing:status(S3),

    tick_n(S3, 31),
    "fault" = servo_homing:status(S3),

    {ok, S4} = servo_homing:start_link(),
    servo_homing:limit_hit(S4),
    "unhomed" = servo_homing:status(S4),
    servo_homing:index_pulse(S4),
    "unhomed" = servo_homing:status(S4),

    io:format("PASS: servo_homing~n"),
    halt(0).

tick_n(_S, 0) -> ok;
tick_n(S, N) ->
    servo_homing:tick(S),
    tick_n(S, N - 1).
