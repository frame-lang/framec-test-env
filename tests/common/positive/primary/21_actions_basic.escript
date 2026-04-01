#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = actions_test:start_link(),
    10 = actions_test:process(Pid, 5),
    Log = actions_test:get_log(Pid),
    true = (string:find(Log, "start") /= nomatch),
    true = (string:find(Log, "done") /= nomatch),
    io:format("PASS: 21_actions_basic~n"),
    halt(0).
