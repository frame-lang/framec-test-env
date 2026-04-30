#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = state_arg_fwd:start_link(),
    0 = state_arg_fwd:process(Pid),
    state_arg_fwd:configure(Pid, 7),
    7 = state_arg_fwd:process(Pid),
    state_arg_fwd:configure(Pid, 42),
    42 = state_arg_fwd:process(Pid),
    io:format("PASS: 65_hsm_forward_state_args~n"),
    halt(0).
