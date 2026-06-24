#!/usr/bin/env escript
%% #119 behavioral driver: the nested fall-through must thread Data and yield a
%% valid gen_statem return (no bad_return_from_state_function), the transition
%% arm must still fire, and state must accumulate to $Locked after 3 failures.
main(_) ->
    io:format("TAP version 14~n1..3~n"),
    {ok, P} = auth:start_link(), auth:frame_init(P),
    auth:verify(P, "wrong"),
    case auth:failures(P) of
        1 -> io:format("ok 1 - fall-through threaded Data (fails=1)~n");
        G1 -> io:format("not ok 1 # got ~p~n", [G1])
    end,
    auth:verify(P, "wrong"), auth:verify(P, "wrong"),
    case element(1, sys:get_state(P)) of
        locked -> io:format("ok 2 - reached locked after 3~n");
        G2 -> io:format("not ok 2 # got ~p~n", [G2])
    end,
    {ok, P2} = auth:start_link(), auth:frame_init(P2),
    auth:verify(P2, "ok"),
    case element(1, sys:get_state(P2)) of
        active -> io:format("ok 3 - transition arm works~n");
        G3 -> io:format("not ok 3 # got ~p~n", [G3])
    end,
    halt(0).
