#!/usr/bin/env escript
main(_) ->
    {ok, Tc} = tool_changer:start_link(),
    "no_tool" = tool_changer:status(Tc),
    "" = tool_changer:attached_tool(Tc),
    0 = tool_changer:is_energized(Tc),

    tool_changer:request_couple(Tc, "drill_8mm"),
    "approaching" = tool_changer:status(Tc),
    "drill_8mm" = tool_changer:attached_tool(Tc),

    tool_changer:lock_confirmed(Tc),
    "coupled" = tool_changer:status(Tc),

    tool_changer:tool_energized(Tc),
    "working" = tool_changer:status(Tc),
    1 = tool_changer:is_energized(Tc),

    tool_changer:request_uncouple(Tc),
    "working" = tool_changer:status(Tc),
    "drill_8mm" = tool_changer:attached_tool(Tc),
    1 = tool_changer:is_energized(Tc),

    tool_changer:tool_deenergized(Tc),
    "coupled" = tool_changer:status(Tc),
    0 = tool_changer:is_energized(Tc),

    tool_changer:request_uncouple(Tc),
    "uncoupling" = tool_changer:status(Tc),

    tool_changer:lock_lost(Tc),
    "no_tool" = tool_changer:status(Tc),
    "" = tool_changer:attached_tool(Tc),

    {ok, Tc2} = tool_changer:start_link(),
    tool_changer:request_couple(Tc2, "router"),
    tool_changer:lock_confirmed(Tc2),
    tool_changer:lock_lost(Tc2),
    "fault" = tool_changer:status(Tc2),

    {ok, Tc3} = tool_changer:start_link(),
    tool_changer:request_couple(Tc3, "saw"),
    tool_changer:lock_confirmed(Tc3),
    tool_changer:tool_energized(Tc3),
    tool_changer:lock_lost(Tc3),
    "fault" = tool_changer:status(Tc3),
    0 = tool_changer:is_energized(Tc3),

    tool_changer:abort(Tc3),
    "no_tool" = tool_changer:status(Tc3),

    {ok, Tc4} = tool_changer:start_link(),
    tool_changer:request_couple(Tc4, "probe"),
    tool_changer:abort(Tc4),
    "no_tool" = tool_changer:status(Tc4),

    {ok, Tc5} = tool_changer:start_link(),
    tool_changer:request_couple(Tc5, "clamp"),
    tool_changer:lock_lost(Tc5),
    "no_tool" = tool_changer:status(Tc5),

    io:format("PASS: tool_changer~n"),
    halt(0).
