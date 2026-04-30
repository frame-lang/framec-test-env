#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = nested_dict:start_link(),
    nested_dict:configure(Pid1, #{"u" => #{"x" => 1, "y" => 2}, "v" => #{"z" => 3}}),
    1 = nested_dict:get_inner(Pid1, "u", "x"),
    Saved = nested_dict:save_state(Pid1),
    {ok, Pid2} = nested_dict:load_state(Saved),
    1 = nested_dict:get_inner(Pid2, "u", "x"),
    2 = nested_dict:get_inner(Pid2, "u", "y"),
    3 = nested_dict:get_inner(Pid2, "v", "z"),
    io:format("PASS: 78_nested_dict_state_arg~n"),
    halt(0).
