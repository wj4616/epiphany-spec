---
node_id: N-ADVERSARIAL
phase: 6
hat: janusian-adversary
exec_type: spawn
branch_label: D
scale_gates: [DEEP]
required_output_sections: [unknown_unknowns, janusian_pairs, triz_breaks]
---

# N-ADVERSARIAL -- Phase 6 / Branch D (Adversarial)

## Role
Three techniques: **unknown-unknowns probe**, **Janusian** (hold opposites simultaneously),
**TRIZ** (contradiction-driven invention).

## Outputs (`stages/N6-ADVERSARIAL.md`)
- `unknown_unknowns`: list of probes that surfaced previously-invisible failure modes.
- `janusian_pairs`: list of `{thesis, antithesis, synthesis_candidate}`.
- `triz_breaks`: list of `{contradiction_pair, resolution_principle}`.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Apply the three adversarial techniques. For each, surface a finding the other
branches would not have produced.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
