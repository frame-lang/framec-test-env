#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = float_state_arg:start_link(),
    R1 = float_state_arg:scale(Pid, 2.0),
    true = (abs(R1 - 2.0) < 1.0e-9),
    float_state_arg:configure(Pid, 0.5),
    R2 = float_state_arg:scale(Pid, 10.0),
    true = (abs(R2 - 5.0) < 1.0e-9),
    float_state_arg:configure(Pid, 2.5),
    R3 = float_state_arg:scale(Pid, 4.0),
    true = (abs(R3 - 10.0) < 1.0e-9),
    io:format("PASS: 68_hsm_float_state_args~n"),
    halt(0).
