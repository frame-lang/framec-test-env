#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = lamp_h_s_m:start_link(),
    0 = lamp_h_s_m:get_brightness(Pid),
    lamp_h_s_m:turn_on(Pid),
    100 = lamp_h_s_m:get_brightness(Pid),
    lamp_h_s_m:set_brightness(Pid, 50),
    50 = lamp_h_s_m:get_brightness(Pid),
    "white" = lamp_h_s_m:get_color(Pid),
    lamp_h_s_m:turn_off(Pid),
    0 = lamp_h_s_m:get_brightness(Pid),
    io:format("PASS: 32_doc_lamp_hsm~n"),
    halt(0).
