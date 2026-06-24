#!/usr/bin/env escript
%% Behavioral driver for the MFA-with-lockout demo (Cookbook 89), exercising
%% nested if / else-if with mixed state mutation and transitions on Erlang.
-define(EQ(N, Got, Want, Desc),
    case Got of Want -> io:format("ok ~p - ~s~n", [N, Desc]);
        _ -> io:format("not ok ~p - ~s # got ~p~n", [N, Got, Desc]) end).
main(_) ->
    io:format("TAP version 14~n1..14~n"),
    {ok, M} = mfa_auth:start_link(), mfa_auth:frame_init(M),
    ?EQ(1, mfa_auth:get_status(M), "idle", "starts idle"),
    mfa_auth:submit_second_factor(M, "123456"),
    ?EQ(2, mfa_auth:get_status(M), "idle", "idle absorbs 2fa"),
    mfa_auth:submit_username(M, "alice"),
    ?EQ(3, mfa_auth:get_status(M), "awaiting_password", "awaiting password"),
    mfa_auth:submit_password(M, "hunter2"),
    ?EQ(4, mfa_auth:get_status(M), "awaiting_2fa", "awaiting 2fa"),
    ?EQ(5, mfa_auth:get_failures(M), 0, "no failures on correct password"),
    mfa_auth:submit_second_factor(M, "123456"),
    ?EQ(6, mfa_auth:get_status(M), "authenticated", "authenticated"),
    mfa_auth:logout(M),
    ?EQ(7, mfa_auth:get_status(M), "idle", "logged out"),

    {ok, M2} = mfa_auth:start_link(), mfa_auth:frame_init(M2),
    mfa_auth:submit_username(M2, "alice"),
    mfa_auth:submit_password(M2, "wrong"),
    ?EQ(8, mfa_auth:get_failures(M2), 1, "1 failure"),
    mfa_auth:submit_password(M2, "wrong"),
    mfa_auth:submit_password(M2, "wrong"),
    mfa_auth:submit_password(M2, "wrong"),
    ?EQ(9, mfa_auth:get_failures(M2), 4, "4 failures"),
    mfa_auth:submit_password(M2, "wrong"),
    ?EQ(10, mfa_auth:get_status(M2), "locked", "locked after 5"),
    mfa_auth:cooldown_elapsed(M2),
    ?EQ(11, mfa_auth:get_status(M2), "idle", "idle after cooldown"),
    ?EQ(12, mfa_auth:get_failures(M2), 4, "partial reset to threshold-1"),

    {ok, M3} = mfa_auth:start_link(), mfa_auth:frame_init(M3),
    mfa_auth:submit_username(M3, "alice"),
    mfa_auth:submit_password(M3, "hunter2"),
    mfa_auth:submit_second_factor(M3, "bad1"),
    mfa_auth:submit_second_factor(M3, "bad2"),
    mfa_auth:submit_second_factor(M3, "bad3"),
    ?EQ(13, mfa_auth:get_status(M3), "awaiting_password", "2fa gave up after 3"),
    ?EQ(14, mfa_auth:get_failures(M3), 1, "one failure bumped"),
    halt(0).
