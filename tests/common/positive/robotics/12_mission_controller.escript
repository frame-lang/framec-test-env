#!/usr/bin/env escript
main(_) ->
    {ok, M} = mission_controller:start_link(),
    "idle" = mission_controller:status(M),

    mission_controller:start_mission(M, "M-1", 3),
    "traveling" = mission_controller:status(M),
    0 = mission_controller:get_site(M),
    3 = mission_controller:get_total(M),

    mission_controller:arrived_at_site(M),
    "inspecting" = mission_controller:status(M),
    1 = mission_controller:get_retries(M),
    mission_controller:inspection_complete(M),
    1 = mission_controller:get_site(M),
    "traveling" = mission_controller:status(M),
    0 = mission_controller:get_retries(M),

    mission_controller:arrived_at_site(M),
    mission_controller:inspection_failed(M),
    "inspecting" = mission_controller:status(M),
    1 = mission_controller:get_site(M),
    2 = mission_controller:get_retries(M),
    mission_controller:inspection_complete(M),
    2 = mission_controller:get_site(M),

    mission_controller:arrived_at_site(M),
    mission_controller:inspection_failed(M),
    mission_controller:inspection_failed(M),
    mission_controller:inspection_failed(M),
    3 = mission_controller:get_site(M),

    mission_controller:arrived_at_site(M),
    "returning" = mission_controller:status(M),

    mission_controller:docked(M),
    "sending_report" = mission_controller:status(M),

    mission_controller:report_sent(M),
    "idle" = mission_controller:status(M),

    {ok, M2} = mission_controller:start_link(),
    mission_controller:start_mission(M2, "M-2", 5),
    mission_controller:arrived_at_site(M2),
    mission_controller:abort(M2),
    "returning" = mission_controller:status(M2),
    mission_controller:docked(M2),
    mission_controller:report_sent(M2),
    "idle" = mission_controller:status(M2),

    io:format("PASS: mission_controller~n"),
    halt(0).
