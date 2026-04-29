---
node_id: N-LATERAL
phase: 6
hat: lateral-creative
exec_type: spawn
branch_label: A
scale_gates: [STANDARD, DEEP]
required_output_sections: [ideas, implicit_requirements]
---

# N-LATERAL -- Phase 6 / Branch A (Lateral)

## Role
Lateral / implicit-requirements pass. Generate ideas that cover requirements
the user has implied but not stated explicitly.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Generate up to N ideas (where N = `--branch-budget` per active mode) that
target *implicit* requirements the user did not state but the system needs.
Surface each as an idea + the implicit requirement it satisfies.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:`
block at the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
