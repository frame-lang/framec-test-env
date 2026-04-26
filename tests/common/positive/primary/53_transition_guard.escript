#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = transition_guard:start_link(),
    transition_guard:run(Pid),
    Trace = transition_guard:get_trace(Pid),
    Expected = "run:before-self-call;do_transition:body;Done:enter;",
    case Trace of
        Expected ->
            io:format("TC5: trace order is exactly [before, body, enter] - PASS~n"),
            io:format("PASS: 53_transition_guard~n"),
            halt(0);
        _ ->
            io:format("FAIL: expected '~s', got '~s'~n", [Expected, Trace]),
            halt(1)
    end.
