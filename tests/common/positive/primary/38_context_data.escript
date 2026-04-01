#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = context_data:start_link(),
    "processed" = context_data:process(Pid, 42),
    "helped" = context_data:helper(Pid),
    io:format("PASS: 38_context_data~n"),
    halt(0).
