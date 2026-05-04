#!/usr/bin/env escript
main(_) ->
    {ok, P} = test:start_link(),
    case test:ready(P) of
        true ->
            io:format("PASS: 92_return_expr_multiline~n"),
            halt(0);
        Other ->
            io:format("FAIL ready(): ~p~n", [Other]),
            halt(1)
    end.
