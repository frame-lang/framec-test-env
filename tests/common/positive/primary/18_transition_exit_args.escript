#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = exit_args:start_link(),
    "init" = exit_args:get_log(Pid),
    exit_args:shutdown(Pid),
    Log = exit_args:get_log(Pid),
    io:format("Log: ~p~n", [Log]),
    true = (string:find(Log, "exit:cleanup") /= nomatch),
    true = (string:find(Log, "enter_done") /= nomatch),
    io:format("PASS: 18_transition_exit_args~n"),
    halt(0).
