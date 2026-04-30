#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = hsm_four_level:start_link(),
    0 = hsm_four_level:drive(Pid),
    hsm_four_level:write_at_level(Pid, 2),
    2222 = hsm_four_level:get_n(Pid),
    2222 = hsm_four_level:drive(Pid),
    io:format("PASS: 61_hsm_four_level~n"),
    halt(0).
