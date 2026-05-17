#!/usr/bin/env escript
main(_) ->
    {ok, W} = web_authn_ceremony:start_link(),
    "idle" = web_authn_ceremony:get_status(W),
    web_authn_ceremony:begin_registration(W, "alice", "example.com"),
    "awaiting_registration" = web_authn_ceremony:get_status(W),
    "alice" = web_authn_ceremony:get_user(W),
    "example.com" = web_authn_ceremony:get_rp(W),
    web_authn_ceremony:registration_response(W, 1, 1, 1),
    "registered" = web_authn_ceremony:get_status(W),
    web_authn_ceremony:registration_response(W, 1, 1, 1),
    "registered" = web_authn_ceremony:get_status(W),

    {ok, W2} = web_authn_ceremony:start_link(),
    web_authn_ceremony:begin_registration(W2, "bob", "example.com"),
    web_authn_ceremony:registration_response(W2, 0, 1, 1),
    "failed" = web_authn_ceremony:get_status(W2),

    {ok, W3} = web_authn_ceremony:start_link(),
    web_authn_ceremony:begin_registration(W3, "carol", "evil.com"),
    web_authn_ceremony:registration_response(W3, 1, 0, 1),
    "failed" = web_authn_ceremony:get_status(W3),

    {ok, W4} = web_authn_ceremony:start_link(),
    web_authn_ceremony:begin_registration(W4, "dave", "example.com"),
    web_authn_ceremony:registration_response(W4, 1, 1, 0),
    "failed" = web_authn_ceremony:get_status(W4),

    {ok, W5} = web_authn_ceremony:start_link(),
    web_authn_ceremony:begin_registration(W5, "eve", "example.com"),
    web_authn_ceremony:timeout(W5),
    "failed" = web_authn_ceremony:get_status(W5),

    {ok, W6} = web_authn_ceremony:start_link(),
    web_authn_ceremony:begin_authentication(W6, "alice", "example.com", 1),
    "awaiting_assertion" = web_authn_ceremony:get_status(W6),
    web_authn_ceremony:assertion_response(W6, 1, 1, 1, 1, 1),
    "authenticated" = web_authn_ceremony:get_status(W6),

    {ok, W7} = web_authn_ceremony:start_link(),
    web_authn_ceremony:begin_authentication(W7, "alice", "example.com", 1),
    web_authn_ceremony:assertion_response(W7, 1, 1, 0, 1, 1),
    "failed" = web_authn_ceremony:get_status(W7),

    {ok, W8} = web_authn_ceremony:start_link(),
    web_authn_ceremony:begin_authentication(W8, "alice", "example.com", 0),
    web_authn_ceremony:assertion_response(W8, 1, 1, 0, 1, 1),
    "authenticated" = web_authn_ceremony:get_status(W8),

    {ok, W9} = web_authn_ceremony:start_link(),
    web_authn_ceremony:begin_authentication(W9, "alice", "example.com", 1),
    web_authn_ceremony:assertion_response(W9, 1, 0, 1, 1, 1),
    "failed" = web_authn_ceremony:get_status(W9),

    {ok, W10} = web_authn_ceremony:start_link(),
    web_authn_ceremony:begin_authentication(W10, "alice", "example.com", 1),
    web_authn_ceremony:assertion_response(W10, 1, 1, 1, 0, 1),
    "failed" = web_authn_ceremony:get_status(W10),

    {ok, W11} = web_authn_ceremony:start_link(),
    web_authn_ceremony:begin_authentication(W11, "alice", "example.com", 1),
    web_authn_ceremony:assertion_response(W11, 1, 1, 1, 1, 0),
    "failed" = web_authn_ceremony:get_status(W11),

    {ok, W12} = web_authn_ceremony:start_link(),
    web_authn_ceremony:begin_authentication(W12, "alice", "example.com", 1),
    web_authn_ceremony:assertion_response(W12, 0, 1, 1, 1, 1),
    "failed" = web_authn_ceremony:get_status(W12),

    web_authn_ceremony:assertion_response(W6, 0, 0, 0, 0, 0),
    "authenticated" = web_authn_ceremony:get_status(W6),

    io:format("PASS: webauthn~n"),
    halt(0).
