# epiphany-spec

Graph-of-Thought brainstorm-to-specification skill. Excavate → Distill → Crystallize.

Trigger: `/epiphany-spec` or explicit "epiphany-spec" mention.

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
| `scripts/session_md_update.py` | Atomic session.md mutator |
| `scripts/ledger_append.py` | Single-writer ledger appender + annotation pickup |
| `scripts/ledger_digest.py` | Deterministic ledger digest emission |
| `scripts/build_prompt.py` | Build a substituted prompt for a module |
| `scripts/spec-chunk-write.sh` | 17-section concat + marker (`--xml` optional) |
| `scripts/finalize-spec.sh` | Atomic copy spec-vN → spec-final |
| `scripts/seed_similarity.py` | Slugify + Jaccard + SHA-256 hash |
| `scripts/cross_run_index.py` | Cross-run FINALIZED index |
| `scripts/compute_completeness.py` | §15 sub-dimensions + min |
| `scripts/dry_run_pipeline.py` | Dispatch sequence predictor |
| `scripts/epiphany_spec.py` | Unified CLI entry (git-style subcommands) |
| `scripts/validate-graph.py` | PRC1 mechanized (5 checks) |
| `scripts/validate-spec-doc.sh` | V-check dispatcher (reads from manifest) |
| `scripts/_module_validators.py` | Shared module invariants (PRC1 + frontmatter lint) |
| `scripts/_yaml_io.py` | Atomic write discipline (tmp+fsync+rename+bak) |
| `scripts/verifications/manifest.json` | V-check registry |
| `scripts/verifications/v*.py` | V1–V8 individual checks |
| `tests/` | pytest + shell tests |

## Adding a new node

1. Copy and edit an existing `modules/N-*.md` as template.
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

See `SKILL.md` for the full MODE + FLAGS table.
