#!/usr/bin/env escript
main(_) ->
    {ok, Pid} = h_s_m_three_levels:start_link(),

    %% Handled at grandchild
    h_s_m_three_levels:handle_at_grandchild(Pid),
    Log1 = h_s_m_three_levels:get_log(Pid),
    true = (string:find(Log1, "gc_handled") /= nomatch),

    %% Forward to child
    h_s_m_three_levels:forward_to_child(Pid),
    Log2 = h_s_m_three_levels:get_log(Pid),
    true = (string:find(Log2, "gc_fwd") /= nomatch),
    true = (string:find(Log2, "child_handled") /= nomatch),

    %% Forward through child to parent
    h_s_m_three_levels:forward_to_parent(Pid),
    Log3 = h_s_m_three_levels:get_log(Pid),
    true = (string:find(Log3, "parent_handled") /= nomatch),

    io:format("PASS: 42_hsm_three_levels~n"),
    halt(0).
