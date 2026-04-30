#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = hsm_if_state_args:start_link(),
    -1 = hsm_if_state_args:classify(Pid, 5),
    hsm_if_state_args:enter_active(Pid, 10),
    0 = hsm_if_state_args:classify(Pid, 5),
    1 = hsm_if_state_args:classify(Pid, 15),
    0 = hsm_if_state_args:classify(Pid, 10),
    hsm_if_state_args:enter_active(Pid, 50),
    0 = hsm_if_state_args:classify(Pid, 15),
    io:format("PASS: 62_hsm_if_state_args~n"),
    halt(0).
