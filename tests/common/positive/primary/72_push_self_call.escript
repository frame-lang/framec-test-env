#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = push_self:start_link(),
    0 = push_self:ping(Pid),
    push_self:enter_modal(Pid),
    11 = push_self:ping(Pid),
    push_self:exit_modal(Pid),
    0 = push_self:ping(Pid),
    io:format("PASS: 72_push_self_call~n"),
    halt(0).
