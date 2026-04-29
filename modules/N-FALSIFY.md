---
node_id: N-FALSIFY
phase: 11
hat: falsifier
exec_type: inline
required_output_sections: [requirements]
---

# N-FALSIFY -- Phase 11 Falsifiability

## Role
For every test-eligible APU (`type in {functional, requirement, behavior}`),
emit an `R-NNN` entry with both `test:` and `break_attempt:`.

## V6 + coverage_falsifiability dependence
- V6 verifies every R-NNN has both fields populated.
- `coverage_falsifiability` = `apus_with_falsifiable_req / total_test_eligible_apus`.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

For each APU with type in {functional, requirement, behavior}, emit one R-NNN.
Both test and break_attempt MUST be non-empty. break_attempt = explicit attempt
to construct a counter-example, with the actual counter-example reasoning.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
