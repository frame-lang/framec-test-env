#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = comp_ops:start_link(),
    true = comp_ops:is_greater(Pid, 10, 5),
    false = comp_ops:is_greater(Pid, 3, 7),
    io:format("PASS: comparison_ops~n"),
    halt(0).
