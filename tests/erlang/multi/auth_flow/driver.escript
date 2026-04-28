#!/usr/bin/env escript
%% Driver for tests/erlang/multi/auth_flow.
%%
%% Tests cross-system auth-result delegation: AuthApp.authenticate
%% delegates to LoginManager.login through the embedded auth field.
%% Good credentials transition the LoginManager to $LoggedIn AND
%% return "ok" — the same handler combines both, exercising the
%% framec frame_transition__/7 reply-value preservation.

main(_) ->
    code:add_patha("."),
    {ok, Pid} = auth_app:start_link(),

    %% Initial state — unauthenticated.
    "unauthenticated" = auth_app:app_status(Pid),

    %% Bad credentials → "denied", state stays $Unauthenticated.
    "denied" = auth_app:authenticate(Pid, "user", "wrong"),
    "unauthenticated" = auth_app:app_status(Pid),

    %% Good credentials → "ok" AND transitions to $Authenticated
    %% via the same call. The frame_transition__/7 reply value
    %% preserves the @@:return through the transition.
    "ok" = auth_app:authenticate(Pid, "admin", "secret"),
    "authenticated" = auth_app:app_status(Pid),

    %% In $Authenticated, further authenticate calls return
    %% "already_authenticated".
    "already_authenticated" = auth_app:authenticate(Pid, "user2", "pw"),

    io:format("ok 1 - auth_flow~n"),
    init:stop().
