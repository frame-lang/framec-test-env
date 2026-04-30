#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = nested_list:start_link(),
    nested_list:configure(Pid1, [[10, 20], [30, 40]]),
    10 = nested_list:first_first(Pid1),
    2 = nested_list:outer_size(Pid1),
    Saved = nested_list:save_state(Pid1),
    {ok, Pid2} = nested_list:load_state(Saved),
    10 = nested_list:first_first(Pid2),
    2 = nested_list:outer_size(Pid2),
    io:format("PASS: 75_nested_list_state_arg~n"),
    halt(0).
