#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = bool_state_arg:start_link(),
    false = bool_state_arg:is_active(Pid),
    bool_state_arg:configure(Pid, true),
    true = bool_state_arg:is_active(Pid),
    bool_state_arg:configure(Pid, false),
    false = bool_state_arg:is_active(Pid),
    bool_state_arg:configure(Pid, true),
    true = bool_state_arg:is_active(Pid),
    io:format("PASS: 67_hsm_bool_state_args~n"),
    halt(0).
