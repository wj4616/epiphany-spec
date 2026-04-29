---
node_id: N-INTENT-LAYER
phase: 3
hat: intent-layerer
exec_type: inline
required_output_sections: [non_goals, in_scope, back_annotated_apu_ids]
---

# N-INTENT-LAYER -- Phase 3 Intent Layering

## Role
**Sole producer of `non_goal: true` flag on `session.md.apus[i]`** (SS22 item 35).
Classify which APUs are out-of-scope and back-annotate them.

## HG2 interaction
Non-goal-listed APUs satisfy HG2 via the "referenced" path (Section 12 surfaces
them). N-SPEC-CONSTRUCT preservation-check refuses to omit any APU not marked
`non_goal: true`.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

For each APU in session.md.apus, decide whether it is in-scope or out-of-scope
for this spec. Out-of-scope APUs get `non_goal: true` AND appear in non_goals
with a reason. In-scope items pass through unchanged.

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
