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
constraint headers. Surface every issue as a structural_finding.

## Decision classification (BUG-8 fix)

Split warnings into two categories:

- **human_decision_warnings:** WARNING-level items that genuinely require
  human judgment (scope trade-offs, ambiguous requirements, conflicting
  stakeholder preferences).
- **auto_fixed_items:** Non-controversial mechanical issues (indentation,
  header style, trailing whitespace, missing punctuation, numbering gaps)
  that the node applies a deterministic fix to directly. Each entry:
  `{issue, fix_applied, section}`.

Auto-fixes are applied to `session.md.section_overrides` directly; they do
NOT pause the gate. Only `human_decision_warnings` are surfaced at the gate.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
