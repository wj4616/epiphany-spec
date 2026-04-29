---
node_id: N-REFINE-QUERY
phase: 11
hat: query-refiner
exec_type: inline
required_output_sections: [reformulated_query, target_apu_id]
---

# N-REFINE-QUERY -- REJECT-items back-edge

## Role
On `[REJECT items: <ids>]` from Phase 12 gate: reformulate the rejected APU
as a fresh question. Then routes to N-FALSIFY (S7 routing order: REFINE-QUERY
first, then FALSIFY).

## Outputs (`stages/N11-REFINE-QUERY.md`)
- `reformulated_query`: text re-statement of the rejected APU as an unresolved question.
- `target_apu_id`: APU-NNN being refined.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

The user rejected APU-{{target_apu_id}}. Restate it as a fresh open question
(no falsifiability assumption). Output reformulated_query.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
