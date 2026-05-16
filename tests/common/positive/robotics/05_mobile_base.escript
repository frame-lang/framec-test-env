#!/usr/bin/env escript
main(_) ->
    {ok, B} = mobile_base:start_link(),
    "teleop_idle" = mobile_base:status(B),

    mobile_base:drive(B, 0.3, 0.0),
    "teleop_driving" = mobile_base:status(B),
    0.3 = mobile_base:get_v(B),

    mobile_base:tick(B),
    mobile_base:tick(B),
    true = abs(mobile_base:get_x(B) - 0.06) < 1.0e-9,

    mobile_base:drive(B, 0.0, 0.0),
    "teleop_idle" = mobile_base:status(B),

    mobile_base:drive(B, 2.0, 0.0),
    0.5 = mobile_base:get_v(B),
    mobile_base:drive(B, 0.0, 0.0),

    mobile_base:drive(B, 0.3, 0.0),
    mobile_base:bumper_hit(B, "front"),
    "protective_stop" = mobile_base:status(B),
    0.0 = mobile_base:get_v(B),

    PosBefore = mobile_base:get_x(B),
    mobile_base:tick(B),
    PosBefore = mobile_base:get_x(B),

    mobile_base:clear_safety(B),
    "teleop_idle" = mobile_base:status(B),

    mobile_base:drive(B, 0.3, 0.0),
    mobile_base:cliff_detected(B),
    "protective_stop" = mobile_base:status(B),
    mobile_base:clear_safety(B),

    mobile_base:drive(B, 0.3, 0.0),
    mobile_base:e_stop(B),
    "e_stop" = mobile_base:status(B),
    mobile_base:clear_e_stop(B),
    "teleop_idle" = mobile_base:status(B),

    mobile_base:set_autonomous(B),
    "auto_idle" = mobile_base:status(B),

    mobile_base:drive(B, 0.3, 0.0),
    "auto_idle" = mobile_base:status(B),

    mobile_base:follow_waypoints(B, 3),
    "auto_driving" = mobile_base:status(B),
    0 = mobile_base:get_wp_index(B),

    tick_until_auto_idle(B, 250),
    "auto_idle" = mobile_base:status(B),
    3 = mobile_base:get_wp_index(B),

    mobile_base:set_teleop(B),
    "teleop_idle" = mobile_base:status(B),
    WpBefore = mobile_base:get_wp_index(B),
    mobile_base:follow_waypoints(B, 5),
    "teleop_idle" = mobile_base:status(B),
    WpBefore = mobile_base:get_wp_index(B),

    io:format("PASS: mobile_base~n"),
    halt(0).

tick_until_auto_idle(_B, 0) -> ok;
tick_until_auto_idle(B, N) ->
    mobile_base:tick(B),
    case mobile_base:status(B) of
        "auto_idle" -> ok;
        _ -> tick_until_auto_idle(B, N - 1)
    end.
