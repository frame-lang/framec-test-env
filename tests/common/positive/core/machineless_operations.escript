#!/usr/bin/env escript
%% Behavioral driver for the machine-less `Calc` system (Erlang). Mirrors the
%% other backends' TAP contract: construct, call add(2,3), expect 5.
main(_) ->
    io:format("TAP version 14~n1..1~n"),
    {ok, Pid} = calc:start_link(),
    case calc:add(Pid, 2, 3) of
        5 -> io:format("ok 1 - machineless add~n");
        G -> io:format("not ok 1 - add # got ~p~n", [G])
    end,
    halt(0).
