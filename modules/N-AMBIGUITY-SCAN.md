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

## Outputs (`stages/N5-AMBIGUITY-SCAN.md`)
- `vague_items`: list of unresolved hedge phrases / pronoun-overload sites.
- `contradictions`: list of APU-pair contradictions.
- `conflict_ledger`: list of `{conflict_id, items: [APU-A, APU-B], status: open|resolved}`.
- `auto_resolved_synonyms`: list of `{group: [...], chosen: term, ratio: <float>}`.
- `deferred_synonyms`: list of `{group, reason}` for N-CLARIFY-LOOP.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Scan session.md.apus for ambiguity, contradictions, synonym groups. Apply the
auto-resolution rule strictly: only count occurrences in input.md, only
auto-resolve at >=70% with N_X >= 2.

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
