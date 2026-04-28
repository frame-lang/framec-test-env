#!/usr/bin/env escript
%% Driver for tests/erlang/multi/auth_flow.
%%
%% Tests cross-system auth-result delegation: AuthApp.authenticate
%% delegates to LoginManager.login through the embedded auth field.
%% The transition to $Authenticated is split into a separate
%% commit_auth/0 call to avoid the framec @@:return + transition
%% combo that drops the return value on Erlang.

main(_) ->
    code:add_patha("."),
    {ok, Pid} = auth_app:start_link(),

    %% Initial state — unauthenticated.
    "unauthenticated" = auth_app:app_status(Pid),

    %% Bad credentials → "denied", state stays $Unauthenticated.
    "denied" = auth_app:authenticate(Pid, "user", "wrong"),
    _ = auth_app:commit_auth(Pid),
    "unauthenticated" = auth_app:app_status(Pid),

    %% Good credentials → "ok", state stays $Unauthenticated until
    %% commit_auth fires the cross-system transition cascade.
    "ok" = auth_app:authenticate(Pid, "admin", "secret"),
    "unauthenticated" = auth_app:app_status(Pid),
    _ = auth_app:commit_auth(Pid),
    "authenticated" = auth_app:app_status(Pid),

    %% In $Authenticated, further authenticate calls return
    %% "already_authenticated".
    "already_authenticated" = auth_app:authenticate(Pid, "user2", "pw"),

    io:format("ok 1 - auth_flow~n"),
    init:stop().
