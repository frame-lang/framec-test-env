#!/usr/bin/env escript
main(_) ->
    Pid1 = domain_list_dict:create(),
    domain_list_dict:push(Pid1, 10),
    domain_list_dict:push(Pid1, 20),
    domain_list_dict:push(Pid1, 30),
    domain_list_dict:put(Pid1, "a", 1),
    domain_list_dict:put(Pid1, "b", 2),
    domain_list_dict:put(Pid1, "c", 3),
    3 = domain_list_dict:size_l(Pid1),
    10 = domain_list_dict:get_at(Pid1, 0),
    3 = domain_list_dict:size_d(Pid1),
    2 = domain_list_dict:get_v(Pid1, "b"),
    Saved = domain_list_dict:save_state(Pid1),
    {ok, Pid2} = domain_list_dict:load_state(Saved),
    %% List order preserved across the round-trip.
    3 = domain_list_dict:size_l(Pid2),
    10 = domain_list_dict:get_at(Pid2, 0),
    20 = domain_list_dict:get_at(Pid2, 1),
    30 = domain_list_dict:get_at(Pid2, 2),
    %% Dict key/value associations preserved across the round-trip.
    3 = domain_list_dict:size_d(Pid2),
    1 = domain_list_dict:get_v(Pid2, "a"),
    2 = domain_list_dict:get_v(Pid2, "b"),
    3 = domain_list_dict:get_v(Pid2, "c"),
    io:format("PASS: 102_persist_domain_list_dict~n"),
    halt(0).
