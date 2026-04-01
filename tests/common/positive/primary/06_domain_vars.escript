#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = domain_vars:start_link(),
    "default" = domain_vars:get_name(Pid),
    domain_vars:set_name(Pid, "Frame"),
    "Frame" = domain_vars:get_name(Pid),
    0 = domain_vars:get_count(Pid),
    domain_vars:inc_count(Pid),
    domain_vars:inc_count(Pid),
    2 = domain_vars:get_count(Pid),
    io:format("PASS: 06_domain_vars~n"),
    halt(0).
