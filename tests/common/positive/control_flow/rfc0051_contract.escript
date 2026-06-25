#!/usr/bin/env escript
mk() -> {ok,P}=flow:start_link(), flow:frame_init(P), P.
-define(ST(P), element(1, sys:get_state(P))).
main(_) ->
    io:format("TAP version 14~n1..10~n"),
    P1=mk(), flow:ex(P1,1), c(1, ?ST(P1)==done andalso flow:va(P1)==0, "ex c=1: exit, trailing skipped"),
    P2=mk(), flow:ex(P2,0), c(2, ?ST(P2)==idle andalso flow:va(P2)==1, "ex c=0: trailing runs"),
    P3=mk(), flow:xfer(P3,7), c(3, ?ST(P3)==done andalso flow:va(P3)==7, "xfer: mutation persists across transition"),
    P4=mk(), flow:cross(P4,0), c(4, flow:va(P4)==2, "cross c=0: a=2"),
    P5=mk(), flow:read_after(P5,1), c(5, flow:va(P5)==5 andalso flow:vb(P5)==15, "read_after c=1: a=5 b=15"),
    P6=mk(), flow:read_after(P6,0), c(6, flow:vb(P6)==10, "read_after c=0: b=10"),
    P7=mk(), flow:nested(P7,1,0), c(7, flow:vd(P7)==1 andalso flow:ve(P7)==1, "nested 1,0: d=1 AND e=1"),
    P8=mk(), flow:nested(P8,0,9), c(8, flow:vd(P8)==0 andalso flow:ve(P8)==1, "nested 0: d=0 e=1"),
    P9=mk(), flow:elif_trail(P9,0,1), c(9, flow:vc(P9)==1 andalso flow:vb(P9)==1, "elif_trail 0,1: c=1 AND b=1"),
    P10=mk(), flow:elif_trail(P10,0,0), c(10, flow:vb(P10)==1, "elif_trail 0,0: b=1"),
    halt(0).
c(N,true,D)->io:format("ok ~p - ~s~n",[N,D]); c(N,_,D)->io:format("not ok ~p - ~s~n",[N,D]).
