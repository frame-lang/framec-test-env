#!/usr/bin/env escript
main(_) ->
    {ok, D} = drone_flight_mode:start_link(),
    "disarmed" = drone_flight_mode:status(D),
    drone_flight_mode:arm(D, 0),
    "disarmed" = drone_flight_mode:status(D),
    drone_flight_mode:arm(D, 1),
    "armed" = drone_flight_mode:status(D),
    drone_flight_mode:takeoff(D, 5.0),
    "taking_off" = drone_flight_mode:status(D),

    tick_until_hovering(D, 10),
    "hovering" = drone_flight_mode:status(D),
    5.0 = drone_flight_mode:altitude(D),

    drone_flight_mode:set_mission(D, 1),
    "on_mission" = drone_flight_mode:status(D),
    drone_flight_mode:mission_complete(D),
    "hovering" = drone_flight_mode:status(D),

    drone_flight_mode:land(D),
    "landing" = drone_flight_mode:status(D),
    drone_flight_mode:touchdown(D),
    "armed" = drone_flight_mode:status(D),

    {ok, D2} = drone_flight_mode:start_link(),
    drone_flight_mode:arm(D2, 1),
    drone_flight_mode:takeoff(D2, 100.0),
    drone_flight_mode:battery_critical(D2),
    "emergency_land" = drone_flight_mode:status(D2),
    "battery" = drone_flight_mode:failsafe_reason(D2),

    {ok, D3} = drone_flight_mode:start_link(),
    drone_flight_mode:arm(D3, 1),
    drone_flight_mode:takeoff(D3, 5.0),
    tick_until_hovering(D3, 10),
    drone_flight_mode:rc_lost(D3),
    "returning" = drone_flight_mode:status(D3),
    drone_flight_mode:home_reached(D3),
    "landing" = drone_flight_mode:status(D3),

    {ok, D4} = drone_flight_mode:start_link(),
    drone_flight_mode:arm(D4, 1),
    drone_flight_mode:takeoff(D4, 5.0),
    tick_until_hovering(D4, 10),
    drone_flight_mode:set_mission(D4, 1),
    drone_flight_mode:gps_lost(D4),
    "altitude_hold" = drone_flight_mode:status(D4),

    {ok, D5} = drone_flight_mode:start_link(),
    drone_flight_mode:arm(D5, 1),
    drone_flight_mode:takeoff(D5, 5.0),
    tick_until_hovering(D5, 10),
    drone_flight_mode:set_mission(D5, 1),
    drone_flight_mode:geofence_breach(D5),
    "returning" = drone_flight_mode:status(D5),
    "geofence" = drone_flight_mode:failsafe_reason(D5),

    {ok, D6} = drone_flight_mode:start_link(),
    drone_flight_mode:battery_critical(D6),
    drone_flight_mode:rc_lost(D6),
    drone_flight_mode:gps_lost(D6),
    drone_flight_mode:geofence_breach(D6),
    "disarmed" = drone_flight_mode:status(D6),

    io:format("PASS: drone_flight~n"),
    halt(0).

tick_until_hovering(_D, 0) -> ok;
tick_until_hovering(D, N) ->
    drone_flight_mode:tick(D),
    case drone_flight_mode:status(D) of
        "hovering" -> ok;
        _ -> tick_until_hovering(D, N - 1)
    end.
