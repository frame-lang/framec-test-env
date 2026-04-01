#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = return_default:start_link(),
    42 = return_default:with_default(Pid),
    99 = return_default:without_default(Pid),
    io:format("PASS: 14_system_return_default~n"),
    halt(0).
