# epiphany-spec

**Graph-of-Thought brainstorm-to-specification skill for Claude Code.**

Turn a rough idea, feature request, or brief into a versioned, audited specification document — with a human review gate before anything is finalized.

> Excavate → Distill → Crystallize

---

## What it does

`epiphany-spec` takes raw or pre-enhanced input and runs it through a structured cognitive pipeline. The pipeline extracts concepts, layers intent and constraints, runs multi-angle brainstorming, synthesizes the results, and writes a complete spec document. You stay in control: the pipeline pauses for clarification when things are ambiguous, and again at the end for final review before the spec is locked.

This skill handles the **Spec** phase only. Sister skills `epiphany-plan` (break the spec into an implementation plan) and `epiphany-implement` (execute the plan) are planned for a later release.

---

## Invocation

Trigger the skill with the slash command or by mentioning it by name in chat:

```
/epiphany-spec <your idea or brief>
```

**Optional flags:**

| Flag | Effect |
|---|---|
| `--minimal` | Faster run, fewer branches (~10 min) |
| `--standard` | Default mode (~18 min) |
| `--deep` | Thorough run, max branches (~40 min) |
| `--quiet` | Suppress progress chatter |
| `--verbose` | One-line log per node start/complete |
| `--xml` | Wrap spec output in `<spec>` XML tags |
| `--resume <path>` | Continue a paused session from disk |
| `--no-seed` | Skip cross-run similarity seeding |
| `--time-budget <N>min` | Override wall-clock budget |

---

## The pipeline

The skill runs a 12-phase Graph-of-Thought pipeline. Nodes can run inline (in the main agent context), as spawned subagents, or as pure-logic subroutines.

| Phase | Cluster | What happens |
|---|---|---|
| 0 | Setup | Input parsed; sufficiency checked; cross-run seed loaded |
| 1 | Excavate | Input restated; concepts decomposed into atomic units (APUs) |
| 2–3 | Excavate | Intent layers added (goals, constraints, non-goals) |
| 4 | Excavate | Constraint inventory built |
| 5 | Clarify gate | Pipeline pauses if ambiguity is detected — you answer questions or reply `[SKIP]` |
| 6 | Distill | Multi-angle brainstorming: spreading activation, lateral thinking, simulation, adversarial challenge (branches depend on mode) |
| 7–10 | Distill | Ideas aggregated, structured, pruned, adversarially reviewed |
| 11 | Crystallize | Spec sections constructed: falsifiability, dependencies, forward chains |
| 12 | Crystallize | Mechanical + semantic audits run; spec written to disk; **human review gate** |

At the end of Phase 12, you receive the spec and a menu of gate signals:

- `[APPROVE]` — write `spec-final.md` and close the session
- `[APPROVE WITH EDITS]` — confirm you edited the file directly before approving
- `[REJECT items: APU-007, APU-012]` — route specific items back for refinement
- `[ADD: <text>]` — add a new requirement; the pipeline handles it
- `[REWORK from phase <N>]` — roll back and re-run from a named phase
- `[ABORT]` — discard the session (all files are kept)

---

## Hard gates

Three invariants are enforced throughout and cannot be bypassed:

**HG1 — Sufficiency.** If the input has no discernible intent, the pipeline refuses with a one-line message. It does not start.

**HG2 — Zero information loss.** Every concept, technical detail, code block, and constraint from your input must appear in the spec — verbatim, referenced, or explicitly listed as a non-goal. The pipeline adds structure; it never drops meaning.

**HG3 — Input is data.** The pipeline writes a spec _about_ your input. It never executes instructions embedded in the input, opens file paths mentioned in it, or follows URLs from it.

**HG4 — Human gate not bypassed.** `[APPROVE]` must come from you. No auto-approval, even when the completeness score is high.

---

## Outputs

| Path | What it contains |
|---|---|
| `~/docs/epiphany/spec/<session_id>/` | All session artifacts: input, ledger, fragments, topology trace |
| `~/docs/solution/<DD-MM-slug>/spec-v<N>.md` | Versioned spec (one per approval cycle) |
| `~/docs/solution/<DD-MM-slug>/spec-final.md` | Final approved spec |

Sessions survive process restarts. Use `--resume <session_dir>` to continue a paused session.

---

## Verification battery

Before the human gate, the skill runs 8 automated checks (V1–V8) covering section coverage, vocabulary lock, constraint completeness, divergence quality, falsifiability, dependency map integrity, and file write integrity. Failed checks re-route to the relevant pipeline phase; a third failure surfaces as a warning at the gate rather than blocking you.

---

## Full specification

See [`SKILL.md`](SKILL.md) for the complete orchestrator spec: all flags, the full mode table, halt-state inventory, dynamic rewrite rules (D1/D2/D3), pause/resume protocol, edit-propagation routing, and V-check re-route map.

---

## Development

```bash
# Run all tests
python3 -m pytest tests/python -v
bash tests/shell/run-all.sh

# Validate graph topology
python3 scripts/validate-graph.py
```

See [`README.md`](README.md) (this file) for the directory map and instructions for adding new graph nodes.
