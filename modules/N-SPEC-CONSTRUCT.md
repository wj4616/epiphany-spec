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

### Required output format

- **section_map:** Ordered array declaring the full output section structure.
  Each entry: `{section_number, section_title, content_source, is_normative}`.
  - `section_number`: supports arbitrary numbering (`5`, `5.5`, `6`, `A`, `B`)
    to honor input-requested structure (BUG-16 fix).
  - `content_source`: key referencing the GRS state lookup table (see
    N-GRS-EXPORT.md source_key list).
  - `is_normative`: `true` for binding spec contract, `false` for advisory/
    appendix content.
  Default: emit the canonical 17-section map if input.md does not request
  a custom structure.
- **sections:** Indexed map `{<section_number>: <markdown body>}` for all
  normative sections declared in `section_map`. Every APU not flagged non_goal
  must appear in some section's body.
- **hints:** Implementation guidance and forward-looking notes that accompany
  but are distinct from the specification sections. Hints are advisory, not
  normative — they guide implementers but don't constrain the spec contract.
- **artifact_refs:** Array of `{artifact_id, referenced_in_section}` linking
  N-ARTIFACT-GENERATOR output into the relevant spec sections.

**Boundary rule:** if a statement describes WHAT the system must do, it goes in
`sections`. If it describes HOW one MIGHT build it, it goes in `hints`.
When uncertain, default to `sections`.

**Schema-adaptive rule (BUG-10 fix):** Do NOT assume a fixed 17-section
output. Read `input.md` for any explicit section requests (e.g., "Appendix C",
"Section 5.5", "Mode Matrix table"). Map these into `section_map` with
appropriate `content_source` values. If `input.md` is silent on structure, use
the canonical 17-section default.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
