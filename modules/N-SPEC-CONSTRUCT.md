---
node_id: N-SPEC-CONSTRUCT
phase: 11
hat: decomposer
exec_type: inline
required_output_sections: [sections, hints]
---

# N-SPEC-CONSTRUCT -- Phase 11 Specification Construction

## Role
Render the binding-layer-ordered spec body (S11). Authoritative section
sequence for `epiphany-plan` consumption.

## Preservation check (HG2)
Refuses to omit any APU not explicitly marked `non_goal: true` (set by
N-INTENT-LAYER at Phase 3). N-SPEC-CONSTRUCT reads `session.md.apus[i].non_goal`
at section-build time.

## V-check re-route interaction (S10)
- V1a/V1b/V7a/V7b -> re-execute this node with section regeneration.
- V2 -> re-execute with vocabulary-lock pass against `session.md.locked_vocabulary`.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Render Sections 3..11, 15, 16 from session.md state. Section structure must
follow S11 binding-layer order (invariants -> interfaces -> behavior ->
implementation hints, then descriptive). Every APU not flagged non_goal
must appear in some section's body.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
