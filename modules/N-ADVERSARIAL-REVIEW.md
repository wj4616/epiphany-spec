---
node_id: N-ADVERSARIAL-REVIEW
phase: 10
hat: adversarial-reviewer
exec_type: inline
required_output_sections: [pre_mortem, what_would_change_our_mind, boring_baseline]
---

# N-ADVERSARIAL-REVIEW -- Phase 10 Adversarial Review

## Role
Pre-mortem + "what would change our mind" + devil's advocate + boring baseline.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Run a pre-mortem on the chosen_idea from N-PRUNE. For each plausible failure,
list mitigation AND any APU IDs the failure mode promotes to invariants
(elevated_to_invariants). Then state what evidence would flip the decision.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
