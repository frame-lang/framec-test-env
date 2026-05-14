#!/usr/bin/env escript
%% Driver for 104_hsm_override_no_forward.ferl. RFC-0019 leaf-override:
%% the start state ($Child) has its own $> with no `=> $^` forward, so
%% only Child's $> runs — $Parent's $> MUST NOT run. Expected log
%% (no parent_enter, no parent state-var init):
%%   "init,child_enter"

-mode(compile).

main(_) ->
    code:add_patha("."),
    Pid = h_s_m_override:create(),

    Log = h_s_m_override:get_log(Pid),
    Expected = "init,child_enter",
    case Log of
        Expected ->
            io:format("ok 1 - 104_hsm_override_no_forward~n");
        _ ->
            io:format(
                "not ok 1 - 104_hsm_override_no_forward~n  expected: ~p~n  got:      ~p~n",
                [Expected, Log]
            ),
            halt(1)
    end.
