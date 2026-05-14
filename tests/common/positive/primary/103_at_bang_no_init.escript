#!/usr/bin/env escript
main(_) ->
    %% Path 1: @@Counter() — factory; $> fires.
    {ok, A} = counter:create(),
    1 = counter:get_lc(A),
    counter:inc(A), counter:inc(A), counter:inc(A),
    3 = counter:get_n(A),
    Blob = counter:save_state(A),

    %% Path 2: @@!Counter() — bare ctor via start_link/0; $> does NOT fire.
    {ok, Fresh} = counter:start_link(),
    0 = counter:get_lc(Fresh),
    0 = counter:get_n(Fresh),

    %% Path 3: @@!Counter() + restore — blob's lc is preserved.
    {ok, Restored} = counter:restore_state(Blob),
    3 = counter:get_n(Restored),
    1 = counter:get_lc(Restored),

    %% Path 4: bare-ctor shell + method call.
    {ok, Naked} = counter:start_link(),
    counter:inc(Naked),
    1 = counter:get_n(Naked),
    0 = counter:get_lc(Naked),

    io:format("PASS: 103_at_bang_no_init~n"),
    halt(0).
