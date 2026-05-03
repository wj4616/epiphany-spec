---
node_id: N-AUTO-RESOLVE
phase: 5
hat: auto-resolver
exec_type: inline
tier: small
required_output_sections: [resolved_items, remaining_human_items, resolution_log]
---

# N-AUTO-RESOLVE -- Phase 5 Auto-Resolution of Trivial Ambiguities

## Role
Reduce human gate burden by auto-resolving non-controversial ambiguities
that N-AMBIGUITY-SCAN detected. Only items with clear default answers are
resolved here; everything else flows forward to N-CLARIFY-LOOP.

## Resolution policies

### Policy A — Mode-name defaults (BUG-7 fix)
If `vague_items` contains open questions about mode names (e.g., "what should
the deep mode be called?"), apply defaults:
- Deep mode default name: `DEEP`
- Standard mode default name: `STANDARD`
- Minimal mode default name: `MINIMAL`
Only resolve if the question is purely nominal and no prior context overrides exist.

### Policy B — Anti-pattern scope defaults (BUG-7 fix)
If `vague_items` contains ambiguity about anti-pattern / adversarial scope,
apply default: `full pipeline` (all phases, all nodes).

### Policy C — Synonym below-threshold tie-breaking
For `deferred_synonyms` where two terms are tied within 10% (e.g., 45% vs 40%):
- Prefer the term that appears in the input's XML `<role>` block.
- If still tied, prefer the shorter term.
- Log the tie-break rationale.

### Policy D — Non-controversial mechanical warnings (BUG-8 fix)
If `human_decision_warnings` from N-SPEC-AUDIT-MECHANICAL (run in prior cycle)
contains only formatting-level items (indentation, header style, trailing
whitespace), apply the suggested fix directly and remove from warnings.

## Output format

- **resolved_items:** Array of `{item_ref, resolution, policy_applied}`.
- **remaining_human_items:** Array of items that still require human judgment
(vague_items minus resolved_items). Forwarded to N-CLARIFY-LOOP.
- **resolution_log:** Timestamped entries for audit trail.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:` block at
the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
