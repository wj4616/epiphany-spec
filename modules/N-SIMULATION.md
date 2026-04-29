---
node_id: N-SIMULATION
phase: 6
hat: simulator
exec_type: spawn
branch_label: C
scale_gates: [DEEP]
required_output_sections: [scenarios, edge_cases, cross_domain_transfers]
---

# N-SIMULATION -- Phase 6 / Branch C (Simulation)

## Role
Three techniques (S4 Phase 6, S22 item 16):
1. **Scenario projection** -- forward-simulate APU consequences under varying conditions.
2. **Edge-case forcing** -- push parameters to boundary values; expose hidden constraints.
3. **Cross-domain transfer** -- map onto an isomorphic domain; simulate outcomes there.

## Outputs (`stages/N6-SIMULATION.md`)
- `scenarios`: list of `{condition_set, projected_outcome, surfaced_assumption}`.
- `edge_cases`: list of `{parameter, boundary_value, exposed_constraint}`.
- `cross_domain_transfers`: list of `{source_domain, target_domain, isomorphism, simulated_outcome}`.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Apply the three simulation techniques in order. Each emit must surface either
a hidden assumption or a previously-undetected constraint.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
