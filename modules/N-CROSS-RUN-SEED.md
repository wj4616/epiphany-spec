---
node_id: N-CROSS-RUN-SEED
phase: 0_5
hat: null
exec_type: no-llm
required_output_sections: [injected_nodes, source_sessions, scan_ts, stopwords_hash]
---

# N-CROSS-RUN-SEED -- Phase 0.5 Cross-Run Seed (no-llm)

## Role
**Pure orchestrator subroutine.** No LLM call. The orchestrator executes the
algorithm in SS8 of the design doc using `scripts/cross_run_index.py` and
`scripts/seed_similarity.py`.

## Algorithm (SS8 steps 1-5)
1. Load index via `cross_run_index.load_or_rebuild(base)`.
2. Read `session.md.topic_slug`.
3. For each prior session, compute `jaccard(slug_tokens(current), slug_tokens(prior))`.
4. Filter `>= --seed-threshold` (default 0.3); sort desc; retain top 3.
5. Load each retained session's `convergent_nodes`; inject with `activation_weight=0.6`
   and `provenance=[prior-session, session_id=<X>, similarity=<S>]`.

## Fallbacks
- Empty archive -> emit `[no-prior-runs]` tag in fragment; `injected_nodes: []`.
- All matches below threshold -> `[no-related-prior-runs]`; `injected_nodes: []`.
- `--no-seed` flag -> unconditional skip; `injected_nodes: []`.
- `--seed-from <session_id>` -> bypass similarity; load named session.
