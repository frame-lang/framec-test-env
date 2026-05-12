#!/usr/bin/env escript
%% Driver for 47_hsm_enter_both.ferl. Asserts the HSM enter cascade
%% fires top-down at startup: when the start state ($Child) extends
%% $Parent, the runtime's `__prepareEnter` walks the chain root-down
%% and fires every $> handler in order.
%%
%% Expected log after create/0 (which fires the start-state
%% cascade via the implicit init transition):
%%   "init,parent_enter,child_enter"

-mode(compile).

main(_) ->
    code:add_patha("."),
    Pid = h_s_m_enter_both:create(),

    Log = h_s_m_enter_both:get_log(Pid),
    Expected = "init,parent_enter,child_enter",
    case Log of
        Expected ->
            io:format("ok 1 - 47_hsm_enter_both~n");
        _ ->
            io:format(
                "not ok 1 - 47_hsm_enter_both~n  expected: ~p~n  got:      ~p~n",
                [Expected, Log]
            ),
            halt(1)
    end.
