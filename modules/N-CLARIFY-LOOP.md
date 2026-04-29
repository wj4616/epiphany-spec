---
node_id: N-CLARIFY-LOOP
phase: 5
hat: clarifier
exec_type: inline
required_output_sections: [open_questions, answers_received]
---

# N-CLARIFY-LOOP -- Phase 5 Clarify-Loop (pause-and-ask)

## Role
For each unresolved item from N-AMBIGUITY-SCAN, formulate ONE clarifying
question. The orchestrator emits the questions block and pauses (state ->
`AWAITING_CLARIFY`). On the user's next message, parse answers (one per
question, ordered or labeled `Q1/Q2/...`).

## Outputs (`stages/N5-CLARIFY-LOOP.md`)
- `open_questions`: list of `{q_id, apu_refs, question_text}`.
- `answers_received`: list of `{q_id, answer_text}` (populated post-resume).

## Skip path
`[SKIP]` reply -> unanswered items append to `session.md.open_questions_queue`
and surface again at Phase 12.

## Pause UX
Orchestrator emits the SS7 Phase-5 prompt block verbatim. No tool calls fire
while state is `AWAITING_CLARIFY`.

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

For each item in `vague_items`, `contradictions`, and `deferred_synonyms`,
write ONE concise clarifying question (<=2 sentences). Reference relevant APU
IDs. Number them Q1, Q2, ...

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
