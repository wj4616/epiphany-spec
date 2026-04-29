---
node_id: N-IDEA-STRUCTURE
phase: 8
hat: idea-structurer
exec_type: inline
required_output_sections: [idea_cards, novelty_risk_plot, shape_tags]
---

# N-IDEA-STRUCTURE -- Phase 8 Idea Structuring + Shape Tagging

## Role
Convert aggregation output into stable idea cards. **Assigns UUID `idea_id`** to
each idea on first-write; ID survives REFRAME instantiations.

## Pre-Phase-8 references (S6, S22 item 26)
Pre-Phase-8 ideas use `(branch_name, branch_local_index)` tuples. On first-write
here, the orchestrator maintains `session.md.pre_idea_id_map: { "<branch>:<idx>": <uuid> }`
for back-reference.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

For each high-confidence convergent idea from N-AGGREGATION, produce an idea
card. Choose exactly ONE shape_tag from the closed set {swap, wrap, split,
merge, invert, defer}.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
