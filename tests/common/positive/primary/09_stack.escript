#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = stack_ops:start_link(),
    "Main" = stack_ops:get_state(Pid),
    "Working in Main" = stack_ops:do_work(Pid),
    stack_ops:push_and_go(Pid),
    "Sub" = stack_ops:get_state(Pid),
    "Working in Sub" = stack_ops:do_work(Pid),
    stack_ops:pop_back(Pid),
    "Main" = stack_ops:get_state(Pid),
    io:format("PASS: 09_stack~n"),
    halt(0).
