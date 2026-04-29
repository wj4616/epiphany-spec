---
node_id: RANDOM-ENTRY
phase: 6
hat: random-injector
exec_type: spawn
required_output_sections: [random_concepts]
---

# RANDOM-ENTRY -- D2 Dynamic Template (de Bono technique 2)

## Role
On D2 fire, generates 5 random concepts; feeds N-AGGREGATION as additional
branch (NOT a replacement of N-SPREADING -- additive).

## Outputs (`stages/RANDOM-ENTRY-<seq>.md`)
- `random_concepts`: list of 5 concept items, each `{concept, why_random, possible_relevance}`.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Generate exactly 5 concepts unrelated to the current problem domain. For each,
add a one-line "why_random" provenance note and a "possible_relevance" hook
that tries to bridge to the problem.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
