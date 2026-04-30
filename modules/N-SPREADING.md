---
node_id: N-SPREADING
phase: 6
hat: spreading-activation
exec_type: spawn
branch_label: B
scale_gates: [MINIMAL, STANDARD, DEEP]
required_output_sections: [activation_map, convergent_nodes, convergent_node_count]
---

# N-SPREADING -- Phase 6 / Branch B (Spreading Activation)

## Role
**M1 activation map.** For each APU seed, fire associated concept chains.
Convergent nodes are flagged where >= 2 chains intersect.

## D2 trigger interaction
- MINIMAL threshold: `convergent_node_count == 0` -> D2 fires.
- STANDARD: `< 3`.
- DEEP: `< 5`.
- D2 re-fires this node with N-DEFIXATION prefix; max 2 re-fires per cycle.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

First, build an activation_map: for each APU in session.md.apus, list the
concept chains it fired and their activation targets. Then identify convergent
nodes: where >= 2 chains intersect, emit a `convergent_nodes` entry with the
intersecting concept, the branches that activated it, and the integer
signal_strength (count of chains that arrived at this concept). signal_strength
MUST be >= 2 for an entry to qualify as convergent. Emit convergent_node_count
as the integer count of entries in convergent_nodes.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
