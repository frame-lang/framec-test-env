#!/usr/bin/env escript
main(_) ->
    {ok, D} = dock_controller:start_link(),
    "discharging" = dock_controller:status(D),

    dock_controller:battery_low(D),
    "seeking" = dock_controller:status(D),

    dock_controller:dock_visible(D, 0.1),
    "aligning" = dock_controller:status(D),

    dock_controller:dock_visible(D, 0.01),
    "making_contact" = dock_controller:status(D),

    dock_controller:contact_made(D),
    "verifying_charge" = dock_controller:status(D),

    dock_controller:charging_started(D),
    "charging" = dock_controller:status(D),

    tick_loop(D, 0),
    "undocking" = dock_controller:status(D),

    dock_controller:undock_complete(D),
    "discharging" = dock_controller:status(D),

    {ok, D2} = dock_controller:start_link(),
    dock_controller:battery_low(D2),
    dock_controller:dock_visible(D2, 0.1),
    dock_controller:dock_lost(D2),
    "discharging" = dock_controller:status(D2),

    {ok, D4} = dock_controller:start_link(),
    dock_controller:battery_low(D4),
    dock_controller:dock_visible(D4, 0.1),
    dock_controller:dock_visible(D4, 0.01),
    dock_controller:contact_made(D4),
    dock_controller:charging_fault(D4),
    "failed" = dock_controller:status(D4),
    dock_controller:battery_low(D4),
    "seeking" = dock_controller:status(D4),

    io:format("PASS: dock_charge~n"),
    halt(0).

tick_loop(_D, 100) -> ok;
tick_loop(D, I) ->
    dock_controller:tick(D),
    case dock_controller:status(D) of
        "undocking" -> ok;
        _ -> tick_loop(D, I + 1)
    end.
