#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = context_reentrant:start_link(),
    "inner_result" = context_reentrant:inner(Pid, 5),
    Result = context_reentrant:outer(Pid, 3),
    io:format("outer(3) = ~p~n", [Result]),
    "inner_result" = Result,
    io:format("PASS: 37_context_reentrant~n"),
    halt(0).
