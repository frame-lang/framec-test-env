#!/usr/bin/env escript
main(_) ->
    {ok, P} = pid_supervisor:start_link(),
    "disabled" = pid_supervisor:status(P),

    0.0 = pid_supervisor:tick(P, 10.0),
    pid_supervisor:set_setpoint(P, 100.0),
    "disabled" = pid_supervisor:status(P),

    pid_supervisor:enable(P),
    "holding" = pid_supervisor:status(P),

    pid_supervisor:set_setpoint(P, 10.0),
    Out1 = pid_supervisor:tick(P, 0.0),
    true = erlang:abs(Out1 - 11.1) < 1.0e-9,
    Iv1 = pid_supervisor:integrator_val(P),
    true = erlang:abs(Iv1 - 10.0) < 1.0e-9,

    Out2 = pid_supervisor:tick(P, 5.0),
    true = erlang:abs(Out2 - 6.45) < 1.0e-9,
    Iv2 = pid_supervisor:integrator_val(P),
    true = erlang:abs(Iv2 - 15.0) < 1.0e-9,

    pid_supervisor:saturate_detected(P),
    "saturated" = pid_supervisor:status(P),
    Out3 = pid_supervisor:tick(P, 6.0),
    true = erlang:abs(Out3 - 3.99) < 1.0e-9,
    Iv3 = pid_supervisor:integrator_val(P),
    true = erlang:abs(Iv3 - 15.0) < 1.0e-9,

    pid_supervisor:clear_saturation(P),
    "holding" = pid_supervisor:status(P),
    Iv4 = pid_supervisor:integrator_val(P),
    true = erlang:abs(Iv4 - 15.0) < 1.0e-9,

    pid_supervisor:start_autotune(P),
    "tuning" = pid_supervisor:status(P),
    pid_supervisor:set_setpoint(P, 50.0),
    "tuning" = pid_supervisor:status(P),

    pid_supervisor:tune_step_done(P),
    "holding" = pid_supervisor:status(P),

    pid_supervisor:disable(P),
    "disabled" = pid_supervisor:status(P),
    0.0 = pid_supervisor:integrator_val(P),

    {ok, P2} = pid_supervisor:start_link(),
    pid_supervisor:enable(P2),
    pid_supervisor:saturate_detected(P2),
    "saturated" = pid_supervisor:status(P2),

    {ok, P3} = pid_supervisor:start_link(),
    pid_supervisor:enable(P3),
    pid_supervisor:start_autotune(P3),
    pid_supervisor:saturate_detected(P3),
    "saturated" = pid_supervisor:status(P3),

    io:format("PASS: pid_supervisor~n"),
    halt(0).
