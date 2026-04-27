#!/usr/bin/env escript
%% Driver for 39_self_call.ferl. Asserts that @@:self.method() routes
%% through frame_dispatch__ and returns the called handler's value.
%% Pattern-match failures cause an Erlang badmatch exception; that
%% exits non-zero, which the runner classifies as test failure.

main(_) ->
    code:add_patha("."),
    {ok, Pid} = self_call_test:start_link(),
    %% get_base/1 returns the literal 42 directly.
    42 = self_call_test:get_base(Pid),
    %% calibrate/1 reentrantly calls get_base via @@:self and propagates
    %% the value out — this is the case the smoke-test driver can't see.
    42 = self_call_test:calibrate(Pid),
    io:format("ok 1 - 39_self_call~n").
