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

## Algorithm
Execute these steps as pure orchestrator logic (no LLM):

1. **D1 evaluation:** invoke
   `python3 scripts/d1_trigger_eval.py --aggregation-fragment <SD>/stages/N7-AGGREGATION.md`
   If `fire: true`, record `D1` in fired_triggers and add entries to
   instantiated_nodes: `{node_id: DOMAIN-TARGETED, reason: coverage gap in <domain_class>,
   trigger_label: D1}` per gap. Schedule N-AGGREGATION re-fire once after all
   DOMAIN-TARGETED outputs land.

2. **D2 evaluation:** read `convergent_node_count` from the most recent
   N-SPREADING fragment, then invoke
   `python3 scripts/d2_trigger_eval.py --count <N> --mode <MODE> --cycle <C> --prior <P>`
   If `fire: true`, record `D2` in fired_triggers and add
   `{node_id: RANDOM-ENTRY, reason: thin spread (count=<N>), trigger_label: D2}`.
   Schedule N-SPREADING re-fire with N-DEFIXATION prefix.

3. **D3 evaluation:** for each idea_id in the current `reframe_seq` group with
   >=2 consecutive scores, invoke
   `python3 scripts/d3_trigger_eval.py --scores <csv> --idea-id <id> --prior-reframes <N>`
   If `action: instantiate-reframe`, record `D3` and add
   `{node_id: REFRAME, reason: score stagnation on <idea_id>, trigger_label: D3}`.
   If `action: skip-reframe-and-queue`, add idea_id to `session.md.open_questions_queue`
   and do NOT instantiate.

4. If `fired_triggers` is non-empty, write the instantiation record to
   `topology-trace.md`: one line per instantiated node with `node_id`, `reason`,
   and `trigger_label`. The orchestrator reads this to insert nodes into the
   active topology overlay before the next ready-set cycle.

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
