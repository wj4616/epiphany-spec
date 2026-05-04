---
node_id: N-AMBIGUITY-SCAN
phase: 5
hat: clarifier
exec_type: inline
required_output_sections: [vague_items, contradictions, conflict_ledger, auto_resolved_synonyms, deferred_synonyms]
---

# N-AMBIGUITY-SCAN -- Phase 5 Ambiguity + Conflict Ledger

## Role
Detect ambiguity, contradictions, and synonym conflicts. Initialize
`session.md.locked_vocabulary` with auto-resolved synonyms.

## Synonym resolution policy (SS4 Phase 5, SS22 item 64)
For a candidate synonym group `{term_A, term_B, ...}` with occurrence counts
`N_A, N_B, ...` in `input.md`:
- **Auto-resolve to `term_X`** iff `N_X / sum(N_*) >= 0.70` AND `N_X >= 2`.
- Single-instance terms (`N_X = 1`) NEVER auto-resolve regardless of ratio.
- Below 70% or single-instance: defer to N-CLARIFY-LOOP.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Scan session.md.apus for ambiguity, contradictions, synonym groups. Apply the
auto-resolution rule strictly: only count occurrences in input.md, only
auto-resolve at >=70% with N_X >= 2.

### Required output format

- **vague_items:** APU IDs or phrases with ambiguous referents. Each entry:
  `{ref, issue, suggested_disambiguation (optional), resolution_recommendation: auto|human}`.
  `resolution_recommendation` classifier (v1.1):
  - `auto` = item has a clear default answer (mode names, scope defaults,
    formatting-only issues). These flow to N-AUTO-RESOLVE.
  - `human` = item requires subjective judgment or domain expertise. These
    flow to N-CLARIFY-LOOP.
- **contradictions:** Direct logical conflicts between APU claims. Each:
  `{apu_a, apu_b, conflict_description}`.
- **conflict_ledger:** Superset of contradictions. Also includes near-conflicts,
  tension pairs, and items flagged for human review. Each entry:
  `{pair: [id_a, id_b], type: contradiction|tension|near_conflict, resolved: false}`.
  The `resolved` field is set to `true` by the orchestrator only after human
  gate resolution — always emit as `false`.
- **auto_resolved_synonyms:** `{canonical: <term>, replaced: [<terms>], confidence: <0.7-1.0>}`.
- **deferred_synonyms:** Groups below 70% threshold — forwarded to N-AUTO-RESOLVE
  for tie-breaking or to N-CLARIFY-LOOP if tie-breaking fails (v1.1).

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
