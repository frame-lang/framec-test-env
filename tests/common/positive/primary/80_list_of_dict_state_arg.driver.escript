#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = list_of_dict:start_link(),
    list_of_dict:configure(Pid1, [#{"x" => 1, "y" => 2}, #{"z" => 3}]),
    1 = list_of_dict:get_at(Pid1, 0, "x"),
    3 = list_of_dict:get_at(Pid1, 1, "z"),
    Saved = list_of_dict:save_state(Pid1),
    {ok, Pid2} = list_of_dict:load_state(Saved),
    1 = list_of_dict:get_at(Pid2, 0, "x"),
    2 = list_of_dict:get_at(Pid2, 0, "y"),
    3 = list_of_dict:get_at(Pid2, 1, "z"),
    io:format("PASS: 80_list_of_dict_state_arg~n"),
    halt(0).
