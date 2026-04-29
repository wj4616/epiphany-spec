---
node_id: N-CONSTRAINT-INVENTORY
phase: 4
hat: constraint-enumerator
exec_type: spawn
required_output_sections: [constraints, enumeration_complete]
---

# N-CONSTRAINT-INVENTORY -- Phase 4 Constraint Inventory

## Role
**M8 = exhaustive enumeration.** Both axes per constraint:
- `statedness \in {Hard, Soft, Ghost}` (Hard = explicitly stated; Soft = explicitly relaxable; Ghost = inferred).
- `severity \in {must, should, nice}`.

For Soft and Ghost constraints, MANDATORY field `solutions_opened_if_removed: [...]`.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

For each constraint implied or stated in session.md.apus, emit a `C-NNN` entry
with both axes (statedness + severity). Soft/Ghost MUST include
`solutions_opened_if_removed`. Set `enumeration_complete: true` only when you
have surveyed every APU of `type: constraint` AND every other APU's implicit
constraints.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:` block at
the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`. The orchestrator picks these up automatically
as `ann-<fragment_prefix>-NNN` in the ledger.
