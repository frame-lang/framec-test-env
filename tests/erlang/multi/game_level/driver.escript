#!/usr/bin/env escript
%% Driver for tests/erlang/multi/game_level.
%%
%% Tests cross-system embedding (GameLevel embeds EnemySpawner) plus
%% state transitions in BOTH systems: GameLevel goes
%% Loading → Playing → Victory while the embedded spawner goes
%% Ready → Exhausted after 3 spawns.

main(_) ->
    code:add_patha("."),
    Pid = game_level:create(),

    %% Initial state — Loading.
    "loading" = game_level:level_status(Pid),

    %% Start → Playing.
    _ = game_level:start(Pid),
    "playing" = game_level:level_status(Pid),

    %% Three spawns: each returns "enemy_spawned" via the embedded
    %% EnemySpawner. The third spawn flips spawner to $Exhausted.
    "enemy_spawned" = game_level:spawn_enemy(Pid),
    "enemy_spawned" = game_level:spawn_enemy(Pid),
    "enemy_spawned" = game_level:spawn_enemy(Pid),

    %% Fourth spawn: spawner is in $Exhausted, returns
    %% "no_more_enemies".
    "no_more_enemies" = game_level:spawn_enemy(Pid),

    %% Complete → Victory.
    _ = game_level:complete(Pid),
    "victory" = game_level:level_status(Pid),

    io:format("ok 1 - game_level~n"),
    init:stop().
