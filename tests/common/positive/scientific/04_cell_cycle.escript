#!/usr/bin/env escript
main(_) ->
    {ok, C} = cell_cycle:start_link(),
    "G1" = cell_cycle:phase(C),
    cell_cycle:dna_damage_detected(C),
    "G1-arrested" = cell_cycle:phase(C),
    cell_cycle:tick(C),
    "G1-arrested" = cell_cycle:phase(C),
    cell_cycle:damage_repaired(C),
    "G1" = cell_cycle:phase(C),
    cell_cycle:nutrients_low(C),
    "G0" = cell_cycle:phase(C),
    cell_cycle:nutrients_restored(C),
    "G1" = cell_cycle:phase(C),
    cell_cycle:apoptosis_signal(C),
    "apoptotic" = cell_cycle:phase(C),
    cell_cycle:tick(C),
    cell_cycle:nutrients_restored(C),
    cell_cycle:damage_repaired(C),
    "apoptotic" = cell_cycle:phase(C),

    {ok, C2} = cell_cycle:start_link(),
    cell_cycle:spindle_misaligned(C2),
    "G1" = cell_cycle:phase(C2),

    io:format("PASS: cell_cycle~n"),
    halt(0).
