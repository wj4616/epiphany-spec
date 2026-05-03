---
node_id: N-VERBATIM-GUARD
phase: 0
hat: verbatim-guardian
exec_type: inline
tier: small
required_output_sections: [locked_verbatim_blocks, verbatim_inventory]
---

# N-VERBATIM-GUARD -- Phase 0 Verbatim Preservation Gate

## Role
Detect and lock verbatim blocks in `input.md` before any paraphrasing occurs.
This is the first line of defense against HG2 zero-information-loss violations.

## Detection heuristics
Scan `input.md` for these verbatim-preservation triggers:
1. **Code blocks** — fenced blocks (```language...```) or indented blocks.
2. **JSON/YAML/XML examples** — blocks containing structured data examples.
3. **Quoted verbatim passages** — text inside quotation marks that carries
design identity (e.g., vocabulary lists, role descriptions, axiom statements).
4. **Enumerated inventories** — numbered or bulleted lists that serve as
canonical reference material (e.g., H.9 vocabulary index, edge-type tables,
mode matrices).
5. **File templates** — blocks labeled as template/appendix content.

## Locking protocol
For each detected verbatim block:
- Assign a `lock_id` (e.g., `VB-001`).
- Record the **exact character range** (start/end line numbers) in `input.md`.
- Compute a **fingerprint** (first 80 chars + last 40 chars + length) for
later verification.
- Flag the block type: `code`, `structured_data`, `quoted_text`, `inventory`,
`template`.

## Output format

- **locked_verbatim_blocks:** Array of `{lock_id, block_type, start_line,
end_line, fingerprint, preservation_reason}`.
- **verbatim_inventory:** Summary table of all locked blocks by category,
with estimated token counts. Used by N-RESTATE to skip paraphrasing and by
V9 for verification.

## HG2 enforcement reminder
Any block tagged as verbatim MUST survive through to the spec output
unchanged in meaning, structure, and ordering. N-RESTATE receives this
list and must not paraphrase locked regions.

## ANNOTATIONS (optional)

If you observe a correction, non-obvious insight, open question, or
cross-reference during this node's work, append a `## annotations:` block at
the END of your fragment with one entry per line:

    ## annotations:
    - [ann-001] correction: brief one-line note
    - [ann-002] observation: another one-line note

Types: `correction`, `observation`, `question`, `link`. IDs zero-padded
sequential starting at `001`.
