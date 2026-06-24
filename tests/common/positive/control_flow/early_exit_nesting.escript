#!/usr/bin/env escript
%% #123: pins early-exit nesting (basic + nested) so the ErlangBlockParserFsm
%% deferred-end fold is proven (these crashed under the old nest_early_exits).
-define(ST(P), element(1, sys:get_state(P))).
mk() -> {ok,P}=early_exit:start_link(), early_exit:frame_init(P), P.
main(_) ->
    io:format("TAP version 14~n1..7~n"),
    P1=mk(), early_exit:basic(P1,1), chk(1, ?ST(P1)==done andalso early_exit:x(P1)==0, "basic c=1"),
    P2=mk(), early_exit:basic(P2,0), chk(2, ?ST(P2)==idle andalso early_exit:x(P2)==1, "basic c=0"),
    P3=mk(), early_exit:nested(P3,1,1), chk(3, ?ST(P3)==done, "nested 1,1"),
    chk(4, early_exit:tb(P3)==0 andalso early_exit:ta(P3)==0, "nested 1,1 no trailing"),
    P4=mk(), early_exit:nested(P4,1,0), chk(5, ?ST(P4)==idle andalso early_exit:tb(P4)==1, "nested 1,0 tb=1"),
    chk(6, early_exit:ta(P4)==0, "nested 1,0 ta=0"),
    P5=mk(), early_exit:nested(P5,0,9), chk(7, early_exit:ta(P5)==1 andalso early_exit:tb(P5)==0, "nested 0 ta=1"),
    halt(0).
chk(N, true, D) -> io:format("ok ~p - ~s~n", [N, D]);
chk(N, _, D) -> io:format("not ok ~p - ~s~n", [N, D]).
