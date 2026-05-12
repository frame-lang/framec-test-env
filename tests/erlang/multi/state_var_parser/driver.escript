#!/usr/bin/env escript
%% Driver for tests/erlang/multi/state_var_parser.
%%
%% Exercises the StateVarParserFsm on representative inputs:
%%   1. "$.varname"       — bare variable read, no assignment.
%%   2. "$.varname = x;"  — assignment with simple expr body.
%%   3. "$.varname == y"  — comparison (NOT assignment).

main(_) ->
    code:add_patha("."),

    %% Case 1: bare variable read.
    Bytes1 = <<"$.varname">>,
    P1 = state_var_parser_fsm:create(),
    _ = state_var_parser_fsm:setup(P1, Bytes1, 0, byte_size(Bytes1)),
    _ = state_var_parser_fsm:do_parse(P1),
    false = state_var_parser_fsm:get_is_assignment(P1),
    9 = state_var_parser_fsm:get_result_end(P1),

    %% Case 2: assignment. ExprScanner from pos past `=` to ';'.
    Bytes2 = <<"$.varname = x;">>,
    P2 = state_var_parser_fsm:create(),
    _ = state_var_parser_fsm:setup(P2, Bytes2, 0, byte_size(Bytes2)),
    _ = state_var_parser_fsm:do_parse(P2),
    true = state_var_parser_fsm:get_is_assignment(P2),
    14 = state_var_parser_fsm:get_result_end(P2),

    %% Case 3: comparison `==` is NOT an assignment.
    Bytes3 = <<"$.varname == y">>,
    P3 = state_var_parser_fsm:create(),
    _ = state_var_parser_fsm:setup(P3, Bytes3, 0, byte_size(Bytes3)),
    _ = state_var_parser_fsm:do_parse(P3),
    false = state_var_parser_fsm:get_is_assignment(P3),
    9 = state_var_parser_fsm:get_result_end(P3),

    io:format("ok 1 - state_var_parser~n"),
    init:stop().
