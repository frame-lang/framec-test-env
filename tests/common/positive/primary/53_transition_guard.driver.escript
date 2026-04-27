#!/usr/bin/env escript
%% Driver for 53_transition_guard.ferl. Asserts the automatic
%% post-self-call transition guard:
%%
%%   $Active.run() {
%%     self.trace ++= "run:before-self-call;"
%%     @@:self.doTransition()             %% <-- transitions to $Done
%%     self.trace ++= "run:after-self-call;"
%%   }
%%
%% After @@:self.doTransition() transitions to $Done, the rest of
%% run() (the "after-self-call" append) MUST NOT execute. Erlang
%% implements this contract via a gen_statem case-expression on
%% Data#data.frame_current_state — see footnote [i] in the runtime
%% capability matrix.
%%
%% Trace must be exactly:
%%   "run:before-self-call;do_transition:body;Done:enter;"
%%
%% Crucially WITHOUT "run:after-self-call;" — that's the assertion.

-mode(compile).

main(_) ->
    code:add_patha("."),
    {ok, Pid} = transition_guard:start_link(),

    transition_guard:run(Pid),

    %% Final state should be $Done.
    Trace = transition_guard:get_trace(Pid),
    Expected = "run:before-self-call;do_transition:body;Done:enter;",
    case Trace of
        Expected ->
            io:format("ok 1 - 53_transition_guard~n");
        _ ->
            io:format(
                "not ok 1 - 53_transition_guard~n  expected: ~p~n  got:      ~p~n",
                [Expected, Trace]
            ),
            halt(1)
    end.
