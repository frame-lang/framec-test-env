#!/usr/bin/env escript
main(_) ->
    {ok, B} = secureboot:start_link(),
    0 = secureboot:get_stage(B),
    secureboot:measurement_extended(B, 0), secureboot:verify_result(B, 1, 1),
    1 = secureboot:get_stage(B),
    secureboot:measurement_extended(B, 1), 1 = secureboot:get_stage(B),
    secureboot:antirollback_check(B, 1), 2 = secureboot:get_stage(B),
    secureboot:verify_result(B, 2, 1), secureboot:measurement_extended(B, 2), secureboot:antirollback_check(B, 1),
    3 = secureboot:get_stage(B),
    secureboot:verify_result(B, 3, 1), secureboot:measurement_extended(B, 3),
    4 = secureboot:get_stage(B),

    {ok, B2} = secureboot:start_link(),
    secureboot:measurement_extended(B2, 0), secureboot:verify_result(B2, 1, 0),
    -1 = secureboot:get_stage(B2),
    secureboot:verify_result(B2, 2, 1), -1 = secureboot:get_stage(B2),

    {ok, B3} = secureboot:start_link(),
    secureboot:measurement_extended(B3, 0), secureboot:verify_result(B3, 1, 1),
    secureboot:measurement_extended(B3, 1), secureboot:antirollback_check(B3, 0),
    -1 = secureboot:get_stage(B3),

    {ok, B4} = secureboot:start_link(),
    secureboot:measurement_extended(B4, 0), secureboot:verify_result(B4, 1, 1),
    secureboot:measurement_extended(B4, 1), secureboot:antirollback_check(B4, 1),
    secureboot:verify_result(B4, 2, 0),
    -2 = secureboot:get_stage(B4),

    {ok, B5} = secureboot:start_link(),
    secureboot:measurement_extended(B5, 0), secureboot:verify_result(B5, 1, 1),
    secureboot:measurement_extended(B5, 1), secureboot:antirollback_check(B5, 1),
    secureboot:verify_result(B5, 2, 1), secureboot:measurement_extended(B5, 2),
    secureboot:antirollback_check(B5, 0),
    -2 = secureboot:get_stage(B5),

    {ok, B6} = secureboot:start_link(),
    secureboot:measurement_extended(B6, 0), secureboot:verify_result(B6, 1, 1),
    secureboot:measurement_extended(B6, 1), secureboot:antirollback_check(B6, 1),
    secureboot:verify_result(B6, 2, 1), secureboot:measurement_extended(B6, 2),
    secureboot:antirollback_check(B6, 1), secureboot:verify_result(B6, 3, 0),
    -2 = secureboot:get_stage(B6),

    {ok, B7} = secureboot:start_link(),
    secureboot:antirollback_check(B7, 1),
    0 = secureboot:get_stage(B7),
    secureboot:measurement_extended(B7, 5),
    0 = secureboot:get_stage(B7),

    {ok, B8} = secureboot:start_link(),
    secureboot:verify_result(B8, 3, 1),
    -1 = secureboot:get_stage(B8),

    io:format("PASS: secure_boot~n"),
    halt(0).
