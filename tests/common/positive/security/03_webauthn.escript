#!/usr/bin/env escript
main(_) ->
    {ok, W} = webauthnceremony:start_link(),
    "idle" = webauthnceremony:get_status(W),
    webauthnceremony:begin_registration(W, "alice", "example.com"),
    "awaiting_registration" = webauthnceremony:get_status(W),
    "alice" = webauthnceremony:get_user(W),
    "example.com" = webauthnceremony:get_rp(W),
    webauthnceremony:registration_response(W, 1, 1, 1),
    "registered" = webauthnceremony:get_status(W),
    webauthnceremony:registration_response(W, 1, 1, 1),
    "registered" = webauthnceremony:get_status(W),

    {ok, W2} = webauthnceremony:start_link(),
    webauthnceremony:begin_registration(W2, "bob", "example.com"),
    webauthnceremony:registration_response(W2, 0, 1, 1),
    "failed" = webauthnceremony:get_status(W2),

    {ok, W3} = webauthnceremony:start_link(),
    webauthnceremony:begin_registration(W3, "carol", "evil.com"),
    webauthnceremony:registration_response(W3, 1, 0, 1),
    "failed" = webauthnceremony:get_status(W3),

    {ok, W4} = webauthnceremony:start_link(),
    webauthnceremony:begin_registration(W4, "dave", "example.com"),
    webauthnceremony:registration_response(W4, 1, 1, 0),
    "failed" = webauthnceremony:get_status(W4),

    {ok, W5} = webauthnceremony:start_link(),
    webauthnceremony:begin_registration(W5, "eve", "example.com"),
    webauthnceremony:timeout(W5),
    "failed" = webauthnceremony:get_status(W5),

    {ok, W6} = webauthnceremony:start_link(),
    webauthnceremony:begin_authentication(W6, "alice", "example.com", 1),
    "awaiting_assertion" = webauthnceremony:get_status(W6),
    webauthnceremony:assertion_response(W6, 1, 1, 1, 1, 1),
    "authenticated" = webauthnceremony:get_status(W6),

    {ok, W7} = webauthnceremony:start_link(),
    webauthnceremony:begin_authentication(W7, "alice", "example.com", 1),
    webauthnceremony:assertion_response(W7, 1, 1, 0, 1, 1),
    "failed" = webauthnceremony:get_status(W7),

    {ok, W8} = webauthnceremony:start_link(),
    webauthnceremony:begin_authentication(W8, "alice", "example.com", 0),
    webauthnceremony:assertion_response(W8, 1, 1, 0, 1, 1),
    "authenticated" = webauthnceremony:get_status(W8),

    {ok, W9} = webauthnceremony:start_link(),
    webauthnceremony:begin_authentication(W9, "alice", "example.com", 1),
    webauthnceremony:assertion_response(W9, 1, 0, 1, 1, 1),
    "failed" = webauthnceremony:get_status(W9),

    {ok, W10} = webauthnceremony:start_link(),
    webauthnceremony:begin_authentication(W10, "alice", "example.com", 1),
    webauthnceremony:assertion_response(W10, 1, 1, 1, 0, 1),
    "failed" = webauthnceremony:get_status(W10),

    {ok, W11} = webauthnceremony:start_link(),
    webauthnceremony:begin_authentication(W11, "alice", "example.com", 1),
    webauthnceremony:assertion_response(W11, 1, 1, 1, 1, 0),
    "failed" = webauthnceremony:get_status(W11),

    {ok, W12} = webauthnceremony:start_link(),
    webauthnceremony:begin_authentication(W12, "alice", "example.com", 1),
    webauthnceremony:assertion_response(W12, 0, 1, 1, 1, 1),
    "failed" = webauthnceremony:get_status(W12),

    webauthnceremony:assertion_response(W6, 0, 0, 0, 0, 0),
    "authenticated" = webauthnceremony:get_status(W6),

    io:format("PASS: webauthn~n"),
    halt(0).
