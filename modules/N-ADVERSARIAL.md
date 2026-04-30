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

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

## unknown_unknowns
Probe for blind-spots: what are we NOT asking that we should be? What
assumptions are we making without realizing it? Surface at least 3 specific
unknowns that, if answered, could change the design direction.

## janusian_pairs
Hold two opposing truths simultaneously. For each pair, state the tension
explicitly and what insight emerges from holding both rather than choosing one.
Minimum 2 pairs.

## triz_breaks
Apply contradiction-driven invention. Identify at least 2 contradictions in the
current design space and resolve each by separation principles (time, space,
scale, condition) rather than tradeoff.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
