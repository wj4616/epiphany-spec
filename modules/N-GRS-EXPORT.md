---
node_id: N-GRS-EXPORT
phase: 12
hat: null
exec_type: inline
required_output_sections: [written_section_paths, canonical_path, user_editable_path]
---

# N-GRS-EXPORT -- Phase 12 GRS Export (no-llm)

## Role
**Pure templating + lookups; no creative judgment.** Maps GRS state to 16 spec
sections + Handoff Bundle (section 17). Applies `session.md.section_overrides`
on top of fragment-source content per S11 routing table.

## Algorithm
1. For each section 1..17, render via S11 source map:
   - 1: `session.md` metadata + `stages/N1-RESTATE.md` intent
   - 2: `session.md.locked_vocabulary`
   - 3: `apus[type=invariant]` + Section 11.1 pre-mortem with non-empty `elevated_to_invariants`
   - 4: `apus[type=interface]`
   - 5: N-SPEC-CONSTRUCT `sections[5]`
   - 6: N-SPEC-CONSTRUCT `hints`
   - 7: N-CONSTRAINT-INVENTORY (both axes)
   - 8: `session.md.apus`
   - 9: `apus[type=assumption]`
   - 10: N-FALSIFY `requirements`
   - 11: N-ADVERSARIAL-REVIEW
   - 12: N-INTENT-LAYER `non_goals`
   - 13: `session.md.open_questions_queue`
   - 14: N-PRUNE recommendation + decision_log + rejected_alternatives
   - 15: N-DEPENDENCY-MAP
   - 16: Provenance map (cross-ref of APU IDs <- lens/branch tags from N-AGGREGATION)
   - 17: `session.md.handoff_bundle` (rendered as Handoff Bundle YAML block)
2. Apply `section_overrides[<N>]` over rendered content.
3. Write each section as `stages/spec-v<V>-section-<SS>.md` (SS = 01..17).
4. Invoke `scripts/spec-chunk-write.sh` to concatenate.

## Section_overrides interaction (S7 routing table)
For sections 3-7, 9-12, 14, 15: override values take precedence over freshly
rendered fragment content. For Section 16: read-only (no overrides). Sections
0/1 have per-subfield routing.
