---
node_id: N-FORWARD-CHAIN-BATCH
phase: 11
hat: aggregator
exec_type: inline
required_output_sections: [chained_implications]
---

# N-FORWARD-CHAIN-BATCH -- Phase 11 Forward Chaining

## Role
Mechanical forward-chaining over APUs + N-FALSIFY requirements. Same cognitive
task in both inline (`apu_count <= 30`) and spawn (`apu_count > 30`) forms -- only
execution mode differs.

## Cap-pressure exception (S4)
DEEP + `apu_count > 30` + any D-trigger fired this cycle: degrade to inline
(frees 1 spawn slot). Log `[FORWARD-CHAIN-BATCH-DEGRADE-INLINE ...]`.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

For each APU and each R-NNN, mechanically derive forward implications onto
other APUs.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
