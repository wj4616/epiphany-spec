---
node_id: N-ARTIFACT-GENERATOR
phase: 11
hat: artifact-generator
exec_type: inline
tier: medium
required_output_sections: [artifacts, artifact_paths]
---

# N-ARTIFACT-GENERATOR -- Phase 11 Artifact Generation

## Role
Generate concrete, copy-pasteable artifacts that the spec references but
does not inline. Runs after N-SPEC-CONSTRUCT so it can read the requested
section structure and artifact inventory.

## Artifact types

### Type A — Concrete JSON examples (BUG-4 fix)
If `input.md` requests JSON examples (e.g., "concrete JSON with 2+ Hat entries"),
read `hats.json` and generate a populated example with at least 2 entries.
Write to `stages/artifact-hats-example.json`.

### Type B — Module file template (BUG-5 fix)
If `input.md` requests a module template (e.g., "Appendix C with template"),
generate a canonical module template following the `modules/N*.md` schema
(YAML frontmatter + markdown body + annotations block).
Write to `stages/artifact-module-template.md`.

### Type C — Edge-table schema appendix (BUG-6 fix)
If `input.md` requests an edge-table appendix (e.g., "Appendix D"), generate
a markdown table of all edges from `graph.json` with fields: id, source,
target, kind, label, gate_condition.
Write to `stages/artifact-edge-table.md`.

### Type D — Smoke test scenarios (BUG-3 fix)
If `input.md` requests smoke tests (e.g., "8 smoke test scenarios"), generate
concrete test scenarios as a markdown checklist.
Write to `stages/artifact-smoke-tests.md`.

### Type E — Self-test harness (BUG-17 fix)
If `input.md` requests a test harness (e.g., "tests/run-smoke-tests.sh"),
generate a bash script that exercises key spec assertions.
Write to `stages/artifact-run-smoke-tests.sh`.

### Type F — Mode matrix table (BUG-19 fix)
If `input.md` requests a mode matrix, generate a pipe table with modes as
rows and feature dimensions as columns.
Write to `stages/artifact-mode-matrix.md`.

## Generation rule
Only generate artifacts explicitly requested in `input.md` or `N-SPEC-CONSTRUCT`
output. Never invent artifacts not grounded in input intent. Each artifact
written to disk MUST be referenced in the spec's relevant section (e.g.,
"See `stages/artifact-hats-example.json`").

## Output format

- **artifacts:** Array of `{artifact_id, artifact_type, description, referenced_in_section}`.
- **artifact_paths:** Array of absolute paths to generated artifact files.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:` block at
the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
