#!/usr/bin/env escript
%% Driver for 49_hsm_enter_exit_params.ferl. Asserts the HSM
%% enter/exit cascade with parameter propagation:
%%
%%   1. goToA("starting")        → ChildA's $> sees "starting"
%%   2. goToSibling("leaving_a")
%%      then ("from_a")          → ChildA's <$ sees "leaving_a";
%%                                 ChildB's $> sees "from_a"
%%   3. goBack("leaving_b")
%%      then ("returning")       → ChildB has NO <$ handler so the
%%                                 reason is dropped; ChildA's $>
%%                                 fires with "returning"
%%
%% The trace is the comma-separated string accumulated in self.log,
%% starting from "init". Each step pattern-matches the expected
%% prefix; mismatch crashes escript with badmatch (non-zero exit).

-mode(compile).

main(_) ->
    code:add_patha("."),
    {ok, Pid} = h_s_m_enter_exit_params:start_link(),

    %% Step 0: starting state
    "Start" = h_s_m_enter_exit_params:get_state(Pid),
    "init" = h_s_m_enter_exit_params:get_log(Pid),

    %% Step 1: enter ChildA via goToA
    h_s_m_enter_exit_params:go_to_a(Pid),
    "ChildA" = h_s_m_enter_exit_params:get_state(Pid),
    "init,childA_enter:starting" = h_s_m_enter_exit_params:get_log(Pid),

    %% Step 2: ChildA → ChildB. Exit cascade fires childA_exit, then
    %% enter cascade fires childB_enter.
    h_s_m_enter_exit_params:go_to_sibling(Pid),
    "ChildB" = h_s_m_enter_exit_params:get_state(Pid),
    "init,childA_enter:starting,childA_exit:leaving_a,childB_enter:from_a"
        = h_s_m_enter_exit_params:get_log(Pid),

    %% Step 3: ChildB → ChildA via goBack. Cascade: ChildB's <$ fires
    %% with "leaving_b", then ChildA's $> fires with "returning".
    %% (Earlier versions of this fixture omitted ChildB's <$ handler,
    %% which silently dropped the exit arg. v4 framec rejects that
    %% as E419 — exit args without a matching `<$()` receiver are an
    %% error — so the handler is now declared.)
    h_s_m_enter_exit_params:go_back(Pid),
    "ChildA" = h_s_m_enter_exit_params:get_state(Pid),
    "init,childA_enter:starting,childA_exit:leaving_a,childB_enter:from_a,childB_exit:leaving_b,childA_enter:returning"
        = h_s_m_enter_exit_params:get_log(Pid),

    io:format("ok 1 - 49_hsm_enter_exit_params~n").
