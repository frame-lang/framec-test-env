#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = p_float:start_link(),
    p_float:configure(Pid1, 3.14159),
    Saved = p_float:save_state(Pid1),
    {ok, Pid2} = p_float:load_state(Saved),
    R = p_float:get_rate(Pid2),
    true = (abs(R - 3.14159) < 1.0e-9),
    io:format("PASS: 69_persist_float_state_arg, rate=~p~n", [R]),
    halt(0).
