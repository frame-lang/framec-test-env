#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = str_state_arg:start_link(),
    "anonymous" = str_state_arg:identify(Pid),
    str_state_arg:configure(Pid, "alice"),
    "alice" = str_state_arg:identify(Pid),
    str_state_arg:configure(Pid, "bob"),
    "bob" = str_state_arg:identify(Pid),
    io:format("PASS: 66_hsm_str_state_args~n"),
    halt(0).
