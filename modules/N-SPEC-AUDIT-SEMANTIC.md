---
node_id: N-SPEC-AUDIT-SEMANTIC
phase: 12
hat: semantic-auditor
exec_type: inline
required_output_sections: [intent_alignment_score, divergence_list]
---

# N-SPEC-AUDIT-SEMANTIC -- Phase 12 Semantic Audit (V7b LLM half)

## Role
Reads `stages/N1-RESTATE.md` (Phase 1 paraphrased intent) AND the latest
`stages/N11-SPEC-CONSTRUCT.md` rendering. Produces `intent_alignment_score`
[0,1] and a `divergence_list`. V7b script-side check ingests this.

## Outputs (`stages/N-SPEC-AUDIT-SEMANTIC.md`)
- `intent_alignment_score`: float [0,1].
- `divergence_list`: list of `{section_number, drift_description, severity}`.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Compare the Phase 1 paraphrased intent against the rendered spec. Score
alignment in [0,1] (higher = closer match). For any drift (added scope,
dropped requirement, changed semantics), add an entry to divergence_list.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
