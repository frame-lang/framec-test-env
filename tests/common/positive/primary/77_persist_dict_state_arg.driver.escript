#!/usr/bin/env escript
main(_) ->
    {ok, Pid1} = persist_dict:start_link(),
    persist_dict:configure(Pid1, #{"a" => 10, "b" => 20}),
    10 = persist_dict:get_v(Pid1, "a"),
    Saved = persist_dict:save_state(Pid1),
    {ok, Pid2} = persist_dict:load_state(Saved),
    10 = persist_dict:get_v(Pid2, "a"),
    20 = persist_dict:get_v(Pid2, "b"),
    io:format("PASS: 77_persist_dict_state_arg~n"),
    halt(0).
