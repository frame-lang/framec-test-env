#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = enter_exit:start_link(),

    %% Initial: enter_a fires on init
    Log1 = enter_exit:get_log(Pid),
    "init,enter_a" = Log1,

    %% Transition A->B: exit_a, enter_b
    enter_exit:next(Pid),
    Log2 = enter_exit:get_log(Pid),
    "init,enter_a,exit_a,enter_b" = Log2,

    %% Transition B->A: enter_a
    enter_exit:next(Pid),
    Log3 = enter_exit:get_log(Pid),
    "init,enter_a,exit_a,enter_b,enter_a" = Log3,

    io:format("PASS: 05_enter_exit~n"),
    halt(0).
