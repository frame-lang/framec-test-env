# 08_macaroon — Erlang skip

framec Erlang codegen has structural gaps lowering case-of / if-else
arms that mix side-effect statements with state transitions (extra
`;` separators, missing function clauses). Local source rewrites
(case-of-with-true/false-arms, brace-form if) hit the same gap.

The recipe is exercised on the other 16 backends. Skipped pending
framec Erlang lowering fix for handler arms of shape:

    case COND of
        true ->
            self.x = ...,        % side-effect statement
            -> $Target;          % transition
        false -> ok
    end
