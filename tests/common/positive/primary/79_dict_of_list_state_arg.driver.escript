#!/usr/bin/env escript
main(_) ->
    Pid1 = dict_of_list:create(),
    dict_of_list:configure(Pid1, #{"a" => [10, 20], "b" => [30, 40, 50]}),
    10 = dict_of_list:get_at(Pid1, "a", 0),
    50 = dict_of_list:get_at(Pid1, "b", 2),
    Saved = dict_of_list:save_state(Pid1),
    {ok, Pid2} = dict_of_list:load_state(Saved),
    10 = dict_of_list:get_at(Pid2, "a", 0),
    20 = dict_of_list:get_at(Pid2, "a", 1),
    50 = dict_of_list:get_at(Pid2, "b", 2),
    io:format("PASS: 79_dict_of_list_state_arg~n"),
    halt(0).
