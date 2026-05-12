#!/usr/bin/env escript
main(_) ->
    Pid = list_state_arg:create(),
    -1 = list_state_arg:first_item(Pid),
    0 = list_state_arg:size(Pid),
    list_state_arg:configure(Pid, [10, 20, 30]),
    10 = list_state_arg:first_item(Pid),
    3 = list_state_arg:size(Pid),
    list_state_arg:configure(Pid, [7]),
    7 = list_state_arg:first_item(Pid),
    1 = list_state_arg:size(Pid),
    io:format("PASS: 73_list_state_arg~n"),
    halt(0).
