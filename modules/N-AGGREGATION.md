---
node_id: N-AGGREGATION
phase: 7
hat: aggregator
exec_type: spawn
join: AND
required_output_sections: [convergent_nodes, contradictions, coverage_gaps]
---

# N-AGGREGATION -- Phase 7 Aggregation (AND-join)

## Role
Aggregate Phase 6 branch outputs. Surface convergent nodes (cross-branch),
contradictions, and **coverage_gaps** (the D1 trigger source).

## Outputs (`stages/N7-AGGREGATION.md` + populates `session.md.convergent_nodes`)
- `convergent_nodes`: same schema as N-SPREADING, but `branches_activated_by` may span all 4 branches.
- `contradictions`: cross-branch contradictions.
- `coverage_gaps`: list of `{domain_class, criticality: float [0,1], rationale}`. Max 5 entries (S6).
  - `criticality` drives D1 cap-overflow priority.

## D1 trigger interaction
Non-empty `coverage_gaps` -> D1 fires. For each gap, orchestrator instantiates
`DOMAIN-TARGETED` with that `domain_class`. After all DOMAIN-TARGETED outputs
ready, N-AGGREGATION re-fires once.

## AND-join coordination (S6)
Wait only on branches in `session.md.active_branches` plus D-trigger additions.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Read all Phase 6 fragments listed in `session.md.active_branches`. Emit
convergent_nodes (cross-branch), contradictions, and up to 5 coverage_gaps
ranked by criticality.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
