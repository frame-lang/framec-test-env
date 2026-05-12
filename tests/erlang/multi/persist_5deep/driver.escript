#!/usr/bin/env escript
%% Wave 8 parity for Erlang — 5-deep nested persist via gen_statem
%% process tree. Each level holds its own counter + a child Pid.
%% Bumps cascade down; values sum up the chain. Tests that the
%% Pid chain survives save/restore — each level's child Pid must
%% be re-spawned via the child's load_state.

main(_) ->
    code:add_patha("."),

    A = l1:create(),
    l1:bump(A),
    l1:bump(A),
    l1:bump(A),
    Pre = l1:value(A),
    case Pre of
        15 -> ok;
        _ ->
            io:format("not ok 1 - persist_5deep # pre: ~p~n", [Pre]),
            halt(1)
    end,

    Saved = l1:save_state(A),
    {ok, B} = l1:load_state(Saved),
    Post = l1:value(B),
    case Post of
        15 -> ok;
        _ ->
            io:format("not ok 1 - persist_5deep # post: ~p~n", [Post]),
            halt(1)
    end,

    l1:bump(B),
    After = l1:value(B),
    case After of
        20 ->
            io:format("ok 1 - persist_5deep~n"),
            init:stop();
        _ ->
            io:format("not ok 1 - persist_5deep # after: ~p~n", [After]),
            halt(1)
    end.
