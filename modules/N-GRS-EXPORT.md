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

## Algorithm (v1.1 — schema-adaptive)

1. **Read the section map** from N-SPEC-CONSTRUCT output
   (`stages/N11-SPEC-CONSTRUCT.md` or session.md.section_map). The section map
   declares the desired output sections as an ordered array:
   `{section_number, section_title, content_source, is_normative}`.
   - If no section_map exists, fall back to the canonical 17-section default
     (preserves backward compatibility).
   - Support arbitrary numbering: `5`, `5.5`, `6`, `A`, `B` etc.

2. **Render each section** by looking up its `content_source`:
   | source_key | GRS state lookup |
   |------------|-------------------|
   | `metadata` | `session.md` metadata + `stages/N1-RESTATE.md` intent |
   | `locked_vocabulary` | `session.md.locked_vocabulary` |
   | `invariants` | `apus[type=invariant]` + pre-mortem |
   | `interfaces` | `apus[type=interface]` |
   | `behavior` | N-SPEC-CONSTRUCT `sections[<N>]` |
   | `hints` | N-SPEC-CONSTRUCT `hints` |
   | `constraints` | N-CONSTRAINT-INVENTORY |
   | `apu_registry` | `session.md.apus` |
   | `assumptions` | `apus[type=assumption]` |
   | `falsifiability` | N-FALSIFY `requirements` |
   | `risk` | N-ADVERSARIAL-REVIEW |
   | `non_goals` | N-INTENT-LAYER `non_goals` |
   | `open_questions` | `session.md.open_questions_queue` |
   | `decision_log` | N-PRUNE recommendation + decision_log |
   | `dependency_map` | N-DEPENDENCY-MAP |
   | `provenance` | cross-ref of APU IDs from N-AGGREGATION |
   | `handoff_bundle` | `session.md.handoff_bundle` |
   | `smoke_tests` | `stages/artifact-smoke-tests.md` |
   | `mode_matrix` | `stages/artifact-mode-matrix.md` |
   | `artifacts` | `stages/N11-ARTIFACT-GENERATOR.md` artifact list |
   | `appendix` | dynamically named appendix from artifact generator |

3. **Apply `section_overrides[<N>]`** over rendered content.
4. **Write each section** as `stages/spec-v<V>-section-<SS>.md`
   (SS = zero-padded section number from the section_map).
5. **Invoke `scripts/spec-chunk-write.sh`** to concatenate in section_map order.

### Required output
After completing the algorithm, populate these fields:

- **written_section_paths:** Array of all `stages/spec-v<V>-section-<SS>.md`
  paths that were written (17 entries, SS=01..17).
- **canonical_path:** Path to the canonical exported file
  (`stages/N-GRS-EXPORT-v<V>.md`) — this is the diff baseline.
- **user_editable_path:** Path to the user-facing copy
  (`stages/spec-v<V>.md`) that the human can edit at gate.

These paths are consumed by the orchestrator for diff computation and gate
signal routing. All paths are relative to the session directory.

## Section_overrides interaction (S7 routing table)
For sections 3-7, 9-12, 14, 15: override values take precedence over freshly
rendered fragment content. For Section 16: read-only (no overrides). Sections
0/1 have per-subfield routing.
