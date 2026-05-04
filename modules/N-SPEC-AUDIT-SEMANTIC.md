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

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Compare the Phase 1 paraphrased intent against the rendered spec. Produce
a decomposed score (v1.1) AND an overall `intent_alignment_score` in [0,1].

## Decomposed dimensions (BUG-14 fix)

- **coverage:** [0,1] — Does the spec address every goal-level item from
  the paraphrased intent?
- **fidelity:** [0,1] — Are technical details, constraints, and verbatim
  blocks preserved without semantic drift?
- **structure:** [0,1] — Does the output section structure match the
  structure requested in input.md?
- **constraint_preservation:** [0,1] — Are all input constraints present
  in the spec, mapped to at least one section or APU?

`intent_alignment_score = min(coverage, fidelity, structure, constraint_preservation)`.

For any drift in any dimension, add an entry to `divergence_list` with the
dimension tag: `{dimension, description, severity}`.

## Targeted re-route guidance (BUG-9 fix)

If `intent_alignment_score < 0.9` (v1.1 threshold), include:
- `primary_failure_dimension`: the dimension with the lowest score.
- `recommended_re_route_node`: the node most likely to repair the drift:
  - `coverage` low → N-SPEC-CONSTRUCT (regenerate sections)
  - `fidelity` low → N-RESTATE + N-VERBATIM-GUARD (re-lock verbatim)
  - `structure` low → N-SPEC-CONSTRUCT (rebuild section map)
  - `constraint_preservation` low → N-CONSTRAINT-INVENTORY

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
