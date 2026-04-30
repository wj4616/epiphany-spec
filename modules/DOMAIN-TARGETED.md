---
node_id: DOMAIN-TARGETED
phase: 7
hat: domain-surveyor
exec_type: spawn
required_output_sections: [targeted_findings, domain_class]
---

# DOMAIN-TARGETED -- D1 Dynamic Template

## Role
Instantiated dynamically per coverage gap from N-AGGREGATION. Surveys a
specific `domain_class` for missing concepts.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

A coverage gap was identified in domain {{domain_class}} with rationale
{{rationale}}. Survey this domain for concepts that should appear in the spec
but currently do not.

### Required output format

- **targeted_findings:** Array of `{concept, relevance, suggested_apu_type}` for
  concepts discovered in the domain survey.
- **domain_class:** Echo back the domain class name the orchestrator gave you.
  Your output MUST include the exact `domain_class` from the orchestrator's
  substitution so cross-references stay consistent.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
