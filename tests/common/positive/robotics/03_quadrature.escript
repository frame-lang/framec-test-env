#!/usr/bin/env escript
main(_) ->
    {ok, Q} = quadrature_decoder:start_link(),
    0 = quadrature_decoder:count(Q),
    "none" = quadrature_decoder:direction(Q),
    0 = quadrature_decoder:errors_count(Q),

    0 = quadrature_decoder:signal(Q, 0, 0),
    0 = quadrature_decoder:count(Q),

    1 = quadrature_decoder:signal(Q, 1, 0),
    1 = quadrature_decoder:signal(Q, 1, 1),
    1 = quadrature_decoder:signal(Q, 0, 1),
    1 = quadrature_decoder:signal(Q, 0, 0),
    4 = quadrature_decoder:count(Q),
    "fwd" = quadrature_decoder:direction(Q),

    -1 = quadrature_decoder:signal(Q, 0, 1),
    -1 = quadrature_decoder:signal(Q, 1, 1),
    -1 = quadrature_decoder:signal(Q, 1, 0),
    -1 = quadrature_decoder:signal(Q, 0, 0),
    0 = quadrature_decoder:count(Q),
    "rev" = quadrature_decoder:direction(Q),

    0 = quadrature_decoder:signal(Q, 1, 1),
    1 = quadrature_decoder:errors_count(Q),

    1 = quadrature_decoder:signal(Q, 1, 0),

    quadrature_decoder:reset(Q),
    0 = quadrature_decoder:count(Q),
    "none" = quadrature_decoder:direction(Q),
    0 = quadrature_decoder:errors_count(Q),

    quadrature_decoder:signal(Q, 1, 0),
    quadrature_decoder:signal(Q, 1, 1),
    quadrature_decoder:signal(Q, 0, 1),
    quadrature_decoder:signal(Q, 0, 0),
    quadrature_decoder:signal(Q, 1, 0),
    quadrature_decoder:signal(Q, 1, 1),
    quadrature_decoder:signal(Q, 0, 1),
    quadrature_decoder:signal(Q, 0, 0),
    7 = quadrature_decoder:count(Q),

    io:format("PASS: quadrature~n"),
    halt(0).
