#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = interface_emitted:start_link(),
    "done" = interface_emitted:do_something(Pid),
    io:format("PASS: interface_handlers_emitted~n"),
    halt(0).
