#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = enter_args:start_link(),
    "init" = enter_args:get_log(Pid),
    enter_args:start(Pid),
    Log = enter_args:get_log(Pid),
    io:format("Log: ~p~n", [Log]),
    true = (string:find(Log, "enter:") /= nomatch),
    io:format("PASS: 17_transition_enter_args~n"),
    halt(0).
