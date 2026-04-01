#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = forward_enter_first:start_link(),
    Log1 = forward_enter_first:get_log(Pid),
    true = (string:find(Log1, "child_enter") /= nomatch),
    forward_enter_first:parent_event(Pid),
    Log2 = forward_enter_first:get_log(Pid),
    true = (string:find(Log2, "parent_event") /= nomatch),
    io:format("PASS: 29_forward_enter_first~n"),
    halt(0).
