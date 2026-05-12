#!/usr/bin/env escript
%% Driver for 48_hsm_exit_handlers.ferl. Asserts the HSM exit
%% cascade fires bottom-up on transition between siblings:
%%
%%   $A => $Parent, $B => $Parent
%%
%%   create → enter $A (parent has no $>, so just "a_enter")
%%   goB        → exit $A ("a_exit"), enter $B ("b_enter")
%%                $Parent is the LCA of A and B so no $Parent exit/enter
%%                fires (it stays in the active chain).
%%   goA        → exit $B (NO `<$` handler, dropped); enter $A ("a_enter")
%%
%% Expected log: "init,a_enter,a_exit,b_enter,a_enter"

-mode(compile).

main(_) ->
    code:add_patha("."),
    Pid = h_s_m_exit_handlers:create(),

    "init,a_enter" = h_s_m_exit_handlers:get_log(Pid),

    h_s_m_exit_handlers:go_b(Pid),
    "init,a_enter,a_exit,b_enter" = h_s_m_exit_handlers:get_log(Pid),

    h_s_m_exit_handlers:go_a(Pid),
    "init,a_enter,a_exit,b_enter,a_enter" = h_s_m_exit_handlers:get_log(Pid),

    io:format("ok 1 - 48_hsm_exit_handlers~n").
