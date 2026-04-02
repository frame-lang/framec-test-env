#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = ternary_expr:start_link(),
    "positive" = ternary_expr:classify(Pid, 5),
    "non_positive" = ternary_expr:classify(Pid, -3),
    io:format("PASS: ternary_expr~n"),
    halt(0).
