#!/usr/bin/env escript
%% Driver for 105_selfcall_from_lifecycle.ferl. F1 regression net:
%% @@:self.tick() called from $A.$> increments count (1), from
%% $A.<$ + $B.$> on go() increments to 3. Pre-fix, the Erlang body
%% processor for $>/<$ didn't pass interface_names to the line
%% classifier, so `self.tick()` was misclassified as a record-field
%% access and emitted as `Data#data.tick();` — invalid Erlang.

-mode(compile).

main(_) ->
    code:add_patha("."),
    Pid = lifecycle_self_call:create(),

    C1 = lifecycle_self_call:get_count(Pid),
    if C1 =/= 1 ->
        io:format("not ok 1 - 105_selfcall_from_lifecycle (TC1)~n  expected: 1~n  got:      ~p~n", [C1]),
        halt(1);
    true -> ok
    end,

    lifecycle_self_call:go(Pid),
    C2 = lifecycle_self_call:get_count(Pid),
    case C2 of
        3 ->
            io:format("ok 1 - 105_selfcall_from_lifecycle~n");
        _ ->
            io:format("not ok 1 - 105_selfcall_from_lifecycle (TC2/TC3)~n  expected: 3~n  got:      ~p~n", [C2]),
            halt(1)
    end.
