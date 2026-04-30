---
node_id: N-PRUNE
phase: 10
hat: pruner
exec_type: inline
required_output_sections: [chosen_idea, rejected_alternatives, tradeoff_matrix, kill_criteria]
---

# N-PRUNE -- Phase 10 Pruning + Tradeoffs

## Role
Pareto + tradeoff matrix + hybrid pass + kill criteria. Single chosen idea + ranked rejects.

## Idea-level rejection re-entry path (S22 item 48)
`[REJECT items: 14.1]` -> orchestrator routes back to THIS node for re-execution
with rejected idea filtered out (NOT to N-REFINE-QUERY/N-FALSIFY).

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Produce the tradeoff matrix, then select a single chosen_idea. Each rejected
alternative MUST have a kill_reason in the kill_criteria section and (if
applicable) `dominated_by`.

### Required output format

**chosen_idea:** The single idea that advances. Include idea_id (UUID), summary,
and why it dominates alternatives.

**rejected_alternatives:** Ranked list with kill_reason per entry (why it was
eliminated) and dominated_by where applicable.

**tradeoff_matrix:** Grid: ideas (rows) vs evaluation dimensions (columns).
Dimensions include at minimum: feasibility, novelty, coverage, risk.

**kill_criteria:** List of criteria used to eliminate each rejected alternative.
Each criterion links to the specific rejected alternative it killed.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
