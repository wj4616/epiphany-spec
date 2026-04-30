---
node_id: N-DECOMPOSE-APU
phase: 2
hat: decomposer
exec_type: inline
required_output_sections: [apus, headline]
---

# N-DECOMPOSE-APU -- Phase 2 Decompose to APUs

## Role
Extract **Atomic Processing Units** (APUs) from `input.md` + `stages/N1-RESTATE.md`.
Every APU carries `source_quote` (verbatim input span) -- HG2 enforcement.

## Type taxonomy
- `functional` / `requirement` / `behavior` are **test-eligible** (feed `coverage_falsifiability`).
- `invariant` feeds Section 3.
- `interface` feeds Section 4.
- `assumption` feeds Section 9.
- `constraint` feeds Section 7.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Decompose the input into APUs per the type taxonomy above. Every APU MUST have
a `source_quote` field with the verbatim text it was extracted from. HG2: every
concept in input.md must end up in some APU OR be flagged for non_goal classification
in Phase 3.

### Required output format

- **apus:** Array of `{id: APU-NNN, type: <taxonomy>, text: <one-line>, source_quote: <verbatim>}`.
- **headline:** A single-line summary (<=120 chars) capturing the core task or
  domain focus extracted from the decomposition. Used by N-CROSS-RUN-SEED for
  topic detection and by the orchestrator for progress summaries.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:` block at
the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`. The orchestrator picks these up automatically
as `ann-<fragment_prefix>-NNN` in the ledger.
