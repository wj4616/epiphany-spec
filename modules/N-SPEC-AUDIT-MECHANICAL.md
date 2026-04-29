---
node_id: N-SPEC-AUDIT-MECHANICAL
phase: 12
hat: mechanical-auditor
exec_type: inline
required_output_sections: [structural_findings, human_decision_warnings]
---

# N-SPEC-AUDIT-MECHANICAL -- Phase 12 Mechanical Audit

## Role
Structural checks with LLM assistance for fuzzy matching. Outputs
`human_decision_warnings` for the gate block.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Audit the rendered spec output (read N-SPEC-CONSTRUCT fragment) for structural
issues: missing section headers, mis-ordered sections, untagged APUs, malformed
constraint headers. Surface every issue as a structural_finding. Surface user-
visible WARNING-level items as human_decision_warnings.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
