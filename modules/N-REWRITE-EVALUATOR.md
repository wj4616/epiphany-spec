---
node_id: N-REWRITE-EVALUATOR
phase: cross-cutting
hat: null
exec_type: inline
required_output_sections: [fired_triggers, instantiated_nodes]
---

# N-REWRITE-EVALUATOR -- Cross-cutting (no-llm)

## Role
After every node completion: evaluate D1, D2, D3 boolean triggers (per S6).
**Writes to `topology-trace.md` ONLY when a trigger fires AND produces an
instantiation** -- not on every no-op evaluation.

## D1 -- Coverage Gap
Trigger: `N-AGGREGATION.coverage_gaps` non-empty.
Action: instantiate `DOMAIN-TARGETED` per gap; re-fire N-AGGREGATION once after
all DOMAIN-TARGETED outputs ready. D1 + D2 co-fire: D1 first.

## D2 -- Thin Spread
Trigger: `N-SPREADING.convergent_node_count` below mode threshold:
- MINIMAL: `= 0`
- STANDARD: `< 3`
- DEEP: `< 5`
Action: re-fire N-SPREADING with N-DEFIXATION prefix; instantiate RANDOM-ENTRY
as additive. Per-cycle re-fire limit: 2.

## D3 -- Score Stagnation
Trigger: `|score_n - score_{n-1}| <= 0.05` across 2 consecutive refinement passes
on the same idea_id, **within the same `reframe_seq` group**.
Action: instantiate REFRAME (max 2 per idea_id; on 3rd skip + add to open_questions_queue).

### Required output format (populated only when triggers fire)

- **fired_triggers:** Array of trigger labels that activated this evaluation
  (e.g. `["D1"]`, `["D2"]`, `["D1", "D2"]`, `[]`). Empty array = no triggers
  fired = normal pass-through. Non-empty = write to `topology-trace.md`.
- **instantiated_nodes:** Array of `{node_id, reason, trigger_label}` for each
  dynamic node instantiated in response to fired triggers. Used by the
  orchestrator to insert nodes into the active topology overlay.
