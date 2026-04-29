---
node_id: N-DEPENDENCY-MAP
phase: 11
hat: dep-mapper
exec_type: inline
required_output_sections: [dependency_edges]
---

# N-DEPENDENCY-MAP -- Phase 11 Dependency Mapping

## Role
LLM-driven rendering of N-FALSIFY's `requirements` into a human-readable
dependency summary (Section 15).

## V check interaction (`coverage_dependency_map`)
Denominator = `len(N-FALSIFY output.requirements)` (S22 item 5). Requirements
absent from this output entirely count as uncovered.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

For each R-NNN in N-FALSIFY output, declare dependency edges: which
requirements it constrains, implies, or conflicts with.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
