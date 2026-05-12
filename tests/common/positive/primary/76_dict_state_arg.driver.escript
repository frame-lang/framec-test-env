#!/usr/bin/env escript
main(_) ->
    Pid = dict_state_arg:create(),
    -1 = dict_state_arg:get_v(Pid, "a"),
    0 = dict_state_arg:size(Pid),
    dict_state_arg:configure(Pid, #{"a" => 10, "b" => 20}),
    10 = dict_state_arg:get_v(Pid, "a"),
    20 = dict_state_arg:get_v(Pid, "b"),
    2 = dict_state_arg:size(Pid),
    dict_state_arg:configure(Pid, #{"x" => 99}),
    99 = dict_state_arg:get_v(Pid, "x"),
    1 = dict_state_arg:size(Pid),
    io:format("PASS: 76_dict_state_arg~n"),
    halt(0).
