---
node_id: REFRAME
phase: 8
hat: reframer
exec_type: spawn
required_output_sections: [reframed_idea, frame_history_entry]
---

# REFRAME -- D3 Dynamic Template

## Role
On D3 stagnation: replace stagnant idea card body. The `idea_id` (UUID)
SURVIVES; only `frame` and `frame_history` mutate.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Idea {{idea_id}} has stagnated under stagnation criterion D3 (|Deltascore| <= 0.05
over 2 passes, same reframe_seq group). Reframe this idea: keep the underlying
problem, change the FRAME (vocabulary, perspective, mechanism). Output a fresh
idea card and append the prior frame to frame_history_entry.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
