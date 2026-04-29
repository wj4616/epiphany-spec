---
node_id: N-SCORE
phase: cross-cutting
hat: scorer
exec_type: inline
required_output_sections: [score, trigger_mode]
---

# N-SCORE -- Cross-cutting Scorer (mixed tier)

## Role (S4 always-on table, S22 item 68)
- **LLM-judged (model-small `scorer` hat)** for **creative-divergence** nodes:
  - Phase 6 branches (LATERAL/SPREADING/SIMULATION/ADVERSARIAL)
  - N-AGGREGATION
  - REFRAME
  - RANDOM-ENTRY
- **Deterministic (no-llm)** for **templating/transformation** nodes:
  `score = populated_required_sections / total_required_sections`
  where a required section counts as populated when its value is:
  - a non-whitespace string >= 10 chars, OR
  - a non-empty list (`len >= 1`), OR
  - a mapping with >= 1 key.

## Trigger
After EVERY node output. Orchestrator selects mode at dispatch time.

## PROMPT TEMPLATE  (LLM-judged path only)

Current ledger digest:
{{ledger_at_dispatch}}

Score the just-completed node's output for semantic quality on a 0..1 scale.
Anchors: 0.0 = vacuous/empty, 0.5 = present but lacks insight, 1.0 = sharp,
contributes new signal. Output `score: <float>` and `trigger_mode: llm`.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
