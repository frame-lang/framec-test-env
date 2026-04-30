#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = op_hsm_state_args:start_link(),
    -1 = op_hsm_state_args:classify(Pid, 5),
    op_hsm_state_args:enter_active(Pid, 10),
    15 = op_hsm_state_args:classify(Pid, 5),
    17 = op_hsm_state_args:classify(Pid, 7),
    op_hsm_state_args:enter_active(Pid, 100),
    105 = op_hsm_state_args:classify(Pid, 5),
    io:format("PASS: 64_operation_hsm_state_args~n"),
    halt(0).
