# epiphany-spec

Graph-of-Thought brainstorm-to-specification skill. Excavate → Distill → Crystallize.

Trigger: `/epiphany-spec` or explicit "epiphany-spec" mention.

Authoritative spec: `~/docs/epiphany/specs/2026-04-27-epiphany-spec-skill-design.md`.

## Directory map

| Path | What lives here |
|---|---|
| `SKILL.md` | Orchestrator — instructions executed by Claude Code |
| `graph.json` | Topology + dynamic-template registry |
| `graph.schema.json` | JSON Schema for graph.json |
| `hats.json` | hat → tier map |
| `schemas/session-md-v1.schema.json` | Schema for per-session `session.md` |
| `modules/N-*.md` | Per-node protocols (frontmatter + prompt + ANNOTATIONS) |
| `scripts/session-init.sh` | 7-step session init (§3) |
| `scripts/session-md-update.sh` | Atomic session.md mutator |
| `scripts/ledger-append.sh` | Single-writer ledger appender + annotation pickup |
| `scripts/spec-chunk-write.sh` | 17-section concat + marker (`--xml` optional) |
| `scripts/finalize-spec.sh` | Atomic copy spec-vN → spec-final |
| `scripts/seed_similarity.py` | Frozen NLTK 3.8 stopwords + Jaccard |
| `scripts/cross_run_index.py` | Cross-run FINALIZED index |
| `scripts/scaffold_module.py` | Module-file generator |
| `scripts/d2_trigger_eval.py` | D2 trigger logic (testable) |
| `scripts/compute_completeness.py` | §15 sub-dimensions + min |
| `scripts/validate-graph.py` | PRC1 mechanized (5 checks) |
| `scripts/validate-spec-doc.sh` | V-check dispatcher |
| `scripts/verifications/v*.py` | V1a–V8 individual checks |
| `tests/` | pytest + shell tests |

## Adding a new node

1. `python3 scripts/scaffold_module.py --node-id N-FOO --phase 7 --hat aggregator --exec-type spawn --required-output-sections alpha,beta`
2. Append the node entry to `graph.json`.
3. If new hat, register in `hats.json`.
4. Add fixture + test under `tests/`.
5. `python3 scripts/validate-graph.py` — PRC1 must pass.

## Run all validators

```bash
python3 -m pytest tests/python -v
bash tests/shell/run-all.sh
python3 scripts/validate-graph.py
```

## Usage flags

See `SKILL.md` § MODE + FLAGS for the full table.
