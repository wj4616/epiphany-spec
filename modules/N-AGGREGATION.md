---
node_id: N-AGGREGATION
phase: 7
hat: aggregator
exec_type: spawn
join: AND
required_output_sections: [convergent_nodes, contradictions, coverage_gaps]
---

# N-AGGREGATION -- Phase 7 Aggregation (AND-join)

## Role
Aggregate Phase 6 branch outputs. Surface convergent nodes (cross-branch),
contradictions, and **coverage_gaps** (the D1 trigger source).

## D1 trigger interaction
Non-empty `coverage_gaps` -> D1 fires. For each gap, orchestrator instantiates
`DOMAIN-TARGETED` with that `domain_class`. After all DOMAIN-TARGETED outputs
ready, N-AGGREGATION re-fires once.

## AND-join coordination (S6)
Wait only on branches in `session.md.active_branches` plus D-trigger additions.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

You are the AGGREGATION node at Phase 7. Your job is to merge the outputs of
multiple parallel Phase 6 branches into a coherent whole. Read the active
branch fragments listed in `session.md.active_branches` (AND-join coordination
per S6).

### Branch output types (normalize into convergent_nodes)

| Branch | What it produces | How to normalize |
|--------|-----------------|------------------|
| LATERAL | `ideas` — novel solution concepts | Extract core concept; tag with `source: lateral`; note novelty mechanism |
| SPREADING | `activation_map` — M1 cognitive activation spread | Map each activated region to a convergent node; tag with `source: spreading` and activation evidence |
| SIMULATION | `scenarios` — future-state walkthroughs | Extract design-level implications from each scenario; tag with `source: simulation` |
| ADVERSARIAL | `triz_breaks` — Janusian + TRIZ contradiction resolutions | Convert each resolution into a convergent node; tag with `source: adversarial` and contradiction pair |

### Required output

Emit three structured sections:

#### 1. convergent_nodes
For each node that appears in 2+ branches, emit:

```
### CN-<NNN> [strength: <F>, branches: <list>]
<One-paragraph synthesis drawing from all contributing branches.>
- Source branches: <space-separated list>
- Contradictions with other nodes: <list or "none">
```

Strength = number of supporting branches / total active branches. Nodes with
strength >= 0.5 are "convergent." Nodes appearing in only 1 branch go into the
appendix as "single-branch observations" (not convergent nodes).

#### 2. contradictions
For pairs of convergent nodes or branch claims that conflict:

```
- [CN-<A>] vs [CN-<B>]: <nature of conflict, one sentence>
  Resolution candidates: <list options or "none identified">
```

If no contradictions found, emit: `(no cross-branch contradictions detected)`

#### 3. coverage_gaps (≤5, ranked by criticality)
Domains or concerns absent from ALL branches. For each:

```
- [gap-<N>] domain_class: <domain name>
  criticality: <HIGH|MEDIUM|LOW>
  evidence: <what was searched, what's missing, one sentence>
```

Gaps with criticality=HIGH trigger D1 (DOMAIN-TARGETED instantiation).
Emit at most 5 gaps. If none, emit: `(no critical coverage gaps)`

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
