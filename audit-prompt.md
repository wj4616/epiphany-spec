# epiphany-spec Enhanced Audit Prompt v2

You are auditing the **epiphany-spec** Graph-of-Thought brainstorm-to-specification skill at `~/.claude/skills/epiphany-spec/`. Current state: v1.0.0, 27 static nodes + 3 dynamic templates, 18 scripts, 303 passing tests, PRC1 clean. This audit finds bugs, hazards, design gaps, potential runtime failures, and improvement opportunities across every dimension.

Conduct the audit in sections. For each finding, report:
- **Severity:** `CRITICAL` (runtime deadlock/crash/data-loss), `HIGH` (wrong output/silent failure/security), `MEDIUM` (robustness/confusion/maintenance hazard), `LOW` (style/nit/cosmetic)
- **Evidence:** file path + line numbers or specific node/edge IDs
- **Fix:** concrete remediation — exact file edit, new logic, or removal

---

## DIMENSION 1 — TOPOLOGY & EDGE GRAPH

Start from `graph.json` and `SKILL.md`. Focus on structural correctness and runtime behavior.

### 1a. AND-Join × Scale-Gate Interaction

Phase 6 branches have heterogeneous `scale_gates`:
- N-SPREADING: `["MINIMAL", "STANDARD", "DEEP"]`
- N-LATERAL: `["STANDARD", "DEEP"]`
- N-SIMULATION: `["DEEP"]`
- N-ADVERSARIAL: `["DEEP"]`

SKILL.md lines 304-314 state the AND-join required-count is dynamic (1/2/4 by mode). Verify:
1. Does the ready-set loop correctly pre-mask scale-gated-out branches so they never block N-AGGREGATION?
2. Does `session-init.sh` F010 `active_branches` computation match the `scale_gates` in graph.json for all three modes? Are there branches where `active_branches` includes a label but `scale_gates` excludes the mode (or vice versa)?
3. What happens if `session.md.active_branches` is corrupted to `["GHOST"]` after PRC1 passes? Is there a post-PRC1 tampering guard between PRC1 and AND-join evaluation?
4. D1 adds DOMAIN-TARGETED outputs as additive AND-join inputs to N-AGGREGATION. There is NO back edge from DOMAIN-TARGETED to N-AGGREGATION in graph.json. The orchestrator handles this in-memory. Is this divergence between static graph and runtime topology documented clearly enough for an orchestrator to implement correctly?

### 1b. Node Connectivity Audit

Map every node to its static edges. Flag:
- **Orphans** (zero incoming forward edges): N-INTAKE (expected), N-CROSS-RUN-SEED (has forward from N-INTAKE — OK), N-REFINE-QUERY (Phase 11 — zero incoming FORWARD edges; only has the back-edge from N-SPEC-AUDIT-SEMANTIC with label `REJECT-items-gate`). Is the invocation chain `gate → [REJECT items] → N-REFINE-QUERY → N-FALSIFY` fully specified?
- **Dead ends** (zero outgoing forward edges): N-SCORE, N-REWRITE-EVALUATOR, N-GRS-EXPORT. For N-GRS-EXPORT: it has the REWORK back-edge to N-INTAKE. Does that back-edge cover `[REWORK from phase N]` for phases 1-12, or only phase 0?
- **Cross-cutting nodes** (phase="cross-cutting"): N-SCORE, N-DEFIXATION, N-REWRITE-EVALUATOR. N-SCORE is described as "LLM-judged for creative-divergence nodes, deterministic for templating/transformation." What mechanism detects which kind a node is? Is it hardcoded or data-driven?

### 1c. Phase Numbering

- Phase "0_5" (N-CROSS-RUN-SEED) is an underscore-delimited string. Audit every script that iterates or sorts by phase (`dry_run_pipeline.py`, `compute_completeness.py`, `validate-spec-doc.sh`) — do they handle string phase values or assume numeric sort?
- **Phase 9 is absent.** The pipeline jumps from Phase 8 to Phase 10. No documentation explains this gap. Is it intentional? If so, document it. If an artifact of renumbering, fix it. Also: `[REWORK from phase 9]` would enter a phase with zero nodes — what does the orchestrator do?

### 1d. Dynamic Template Lifecycle

DOMAIN-TARGETED, RANDOM-ENTRY, REFRAME templates exist in `dynamic_templates` but not in the `nodes` array.
1. Does PRC1 mechanized check (`_module_validators.py`) iterate `dynamic_templates` for module completeness (PRC1.1), ledger placeholder (PRC1.2), and MCP references (PRC1.3)? Or does it only iterate `graph["nodes"]`?
2. Does `dry_run_pipeline.py` account for dynamic template spawns when predicting spawn budget? Or does it underestimate?
3. D1 DOMAIN-TARGETED → AGG re-fire, D2 RANDOM-ENTRY → AGG (additive), D3 REFRAME → idea replacement — none of these runtime edges exist in graph.json. Is this divergence intentional and clearly documented?

### 1e. Dead Paths

Identify nodes that can NEVER fire under specific configurations:
- N-LATERAL at MINIMAL: masked by `scale_gates` AND `branch_label`
- N-SIMULATION at MINIMAL/STANDARD: masked by `scale_gates`
- N-ADVERSARIAL at MINIMAL/STANDARD: masked by `scale_gates`
- N-DEFIXATION: only via D2 trigger
- N-REFINE-QUERY: only via `[REJECT items: ...]` gate signal
- REFRAME (dynamic): only via D3 stagnation
- RANDOM-ENTRY (dynamic): only via D2 thin-spread
- DOMAIN-TARGETED (dynamic): only via D1 coverage gap

Are all of these intentionally conditional, or are any accidental dead paths from incorrect edge wiring?

---

## DIMENSION 2 — MODULE PROMPT QUALITY

Read all 27 `modules/N-*.md` + 3 `modules/{DOMAIN-TARGETED,RANDOM-ENTRY,REFRAME}.md` files.

### 2a. Required Output × Prompt Mismatches

For EACH module, verify that every field in `required_output_sections` appears somewhere in the prompt body with structural guidance. Known gaps from prior audits (some may have been fixed):

| Module | Suspect Field | Check |
|---|---|---|
| N-PRUNE | `kill_criteria` | Does the prompt body mention this? Or is it implicit from `kill_reason` sub-fields? |
| N-CLARIFY-LOOP | `answers_received` | Who populates this — the LLM or the orchestrator? If the orchestrator, should it be in required_output_sections? |
| N-DECOMPOSE-APU | `headline` | Is the LLM told what format/content `headline` should have? |
| N-INTENT-LAYER | `in_scope`, `back_annotated_apu_ids` | Are these described in the prompt body? |
| N-AMBIGUITY-SCAN | `conflict_ledger` vs `contradictions` | Is the distinction between these two fields clear to the LLM? |
| N-AGGREGATION | `convergent_nodes` methodology | Does the prompt explain HOW to find convergence across heterogeneous branch outputs? |
| N-IDEA-STRUCTURE | boundary from N-AGGREGATION | N-AGGREGATION produces "convergent nodes" but N-IDEA-STRUCTURE expects "convergent ideas." Is the ontological jump explicit? |
| N-SPEC-CONSTRUCT | `hints` vs `sections` | Is the boundary between these two output sections clear? |
| N-REFINE-QUERY | `target_apu_id` echo | This appears as both `{{target_apu_id}}` input AND required output. Is the LLM told to echo it? |
| DOMAIN-TARGETED | `domain_class` echo | Same input/output overlap as N-REFINE-QUERY. |
| N-GRS-EXPORT | `written_section_paths`, `canonical_path`, `user_editable_path` | Are these named in the algorithm body? (no-llm node) |
| N-REWRITE-EVALUATOR | `fired_triggers`, `instantiated_nodes` | Are these named in the body? (no-llm node) |

For each: if missing, assess downstream impact. Does `spec-chunk-write.sh` crash? Does N-AGGREGATION produce garbage? Does the gate silently omit a required section?

### 2b. Vague / Underspecified Prompts

Flag any module whose prompt body is under 3 sentences or lacks output structure guidance. Especially check:
- N-ADVERSARIAL (now enhanced — verify the enhancement is sufficient for a spawned large-tier agent to produce all three required sections)
- N-AGGREGATION (cross-branch convergence detection — is methodology specified?)
- N-FORWARD-CHAIN-BATCH (mechanical chaining — is the output format specified?)

### 2c. Frontmatter × Body Contradictions

- N-FORWARD-CHAIN-BATCH: `exec_type: inline` in frontmatter but body describes both inline and spawn forms. Does frontmatter now include `exec_type_alternatives` and `exec_decision` fields?
- N-CLARIFY-LOOP: `answers_received` ownership ambiguity (LLM vs orchestrator). Is `answers_received` truly a required LLM output, or should the orchestrator manage it?
- Any module where `exec_type: spawn` but the prompt body assumes inline access to full session context?

### 2d. Cross-Module Data Contract Compatibility

Trace the data flow between adjacent nodes in the forward chain:
- N-DECOMPOSE-APU → N-INTENT-LAYER: APU list consumed correctly?
- Phase 6 branches → N-AGGREGATION: all four produce heterogeneous output types. Does N-AGGREGATION's prompt define how to merge them?
- N-AGGREGATION → N-IDEA-STRUCTURE: "convergent node" → "convergent idea" elevation. Is the transformation explicit?
- N-PRUNE → N-ADVERSARIAL-REVIEW: `chosen_idea` consumed correctly?
- N-ADVERSARIAL-REVIEW → N-FALSIFY: N-FALSIFY reads `session.md.apus` not N-ADVERSARIAL-REVIEW output. Is the edge ordering correct even though there's no direct data dependency?

### 2e. Dangling References

Check for references to files, sections, or concepts that don't exist:
- "S3" / "S4" / "S6" / "S7" / "S11" / "S22" / "S32" / "SS8" / "SS16" / "SS22" — these appear across dozens of modules and SKILL.md. Do they resolve to anything?
- "design brief" referenced in SKILL.md line 48 and elsewhere. Does it exist?
- Any module referencing `stages/N*.md` files that the corresponding node doesn't actually produce?

---

## DIMENSION 3 — SCRIPTS & SECURITY

### 3a. Command Injection & Path Traversal

For every script that accepts user-controlled input, verify:
1. `session-init.sh` `--date` flag (line 34): is the format validated before interpolation into `OUT_BASE`? Can `../` or spaces create path traversal?
2. `finalize-spec.sh` `--version` flag (line 17-18): is version validated as integer before constructing `SRC="$SD/spec-v${VERSION}.md"`?
3. `ledger_append.py` `--fragment` arg (line 66): is the fragment path validated to stay within `session_dir`? Can `../` traverse out?
4. `ledger_append.py` `--signals` and `--provenance-tags` (lines 71-72): are these parsed as JSON and validated before YAML interpolation? Can a newline or `}` character corrupt the ledger YAML block?
5. `session-init.sh` `--flags` (line 101): can `$FLAGS` content containing `"` or newline corrupt the YAML output?
6. Any script using `shell=True` in subprocess calls? Any `eval()` or `exec()`?

### 3b. Atomicity & Durability

1. `_yaml_io.py` `atomic_write_text`: uses `tmp+fsync+rename`. Is `os.replace` atomic on the target filesystem? Is the `.bak` created AFTER the replace (best-effort) — document this.
2. `ledger_append.py` (lines 116-119): appends multi-line YAML blocks to `grs-ledger.md`. POSIX atomic write guarantee only up to `PIPE_BUF` (4096 bytes). Can concurrent `ledger_append.py` invocations interleave blocks? Is there file locking?
3. `spec-chunk-write.sh` (lines 51-52): concatenation uses `cp` (non-atomic). If the system crashes mid-copy, is the canonical or user copy recoverable?
4. `session_md_update.py` `--increment`: does the read-increment-write cycle have a TOCTOU race if two processes increment simultaneously?

### 3c. TOCTOU Races

1. `session-init.sh` lines 47-53: `[ -e "$SD" ]` check then `mkdir -p`. Can an attacker create a symlink between check and mkdir?
2. `session-init.sh` lines 77-81: loop-pick-then-mkdir pattern for solution directory naming. Collision window between loop exit and `mkdir`.
3. Any other check-then-use patterns in `cross_run_index.py` or `validate-spec-doc.sh`?

### 3d. Error Handling

1. `cross_run_index.py` `_safe_load_session_md` (line 24): catches bare `Exception`. Does this swallow `KeyboardInterrupt`, `AttributeError`, `NameError`?
2. `cross_run_index.py` `load_or_rebuild` (line 62): catches bare `Exception` on `json.load`. Does this silently mask `JSONDecodeError`? Is corrupted-index failure logged?
3. `_module_validators.py` `parse_frontmatter` (line 28-34): `yaml.safe_load` without try/except. Does malformed YAML frontmatter crash `validate-graph.py` entirely, skipping all subsequent checks?
4. `build_prompt.py` `_ledger_digest` (lines 29-36): `subprocess.run(..., check=True)` raises `CalledProcessError` on failure. Does this propagate as a user-friendly error or a raw traceback?
5. `v3_constraint_completeness.py` (line 27-31): `Path("")` when `input_md_path` is empty represents CWD. Does this silently read from the wrong directory?
6. `v4_convergent_node_detection.py` (line 19): `int(c.get("signal_strength", 0))` — crashes with `ValueError` on non-numeric string values.
7. `v7b_intent_alignment.py` (line 17): `float(data.get(...))` — same crash pattern on non-numeric strings.

### 3e. Import & Execution Correctness

1. `sys.path.insert(0, str(repo_root))` pattern in 5+ scripts: can a file named `yaml.py` in the repo root shadow the real PyYAML?
2. Every script invoked via `python3 scripts/X.py` from repo root — does it resolve all imports? Run each script's `--help` from `/tmp` to detect missing `sys.path` setup.
3. Flag name consistency: most scripts accept `--session-dir` (directory). `compute_completeness.py` accepts `--session-md` (file path). Is this inconsistency documented?
4. `d2_trigger_eval.py` `--mode`: accepts any string, silently falls back to STANDARD on unrecognized values. Should it use `choices=["MINIMAL", "STANDARD", "DEEP"]`?
5. `session_md_update.py` `--value`: empty string `""` is a valid value (sets field to empty). Is there a way to set a field to YAML `null`? Document the empty-string behavior.

### 3f. ARG_MAX & Buffer Overflow

- `session-init.sh` previously used `$(cat "$SD/input.md")` in command substitution (ARG_MAX risk). Was this fixed?
- `ledger_digest.py` caps output at `--max-bytes 8192`. Is the byte-cap safe with multi-byte UTF-8 at the boundary?
- Any other place where unbounded input could hit OS limits?

---

## DIMENSION 4 — ORCHESTRATOR (SKILL.md) COHERENCE

### 4a. Undefined External References

SKILL.md references these entities. For each, determine: do they exist? If not, is the orchestrator implementable without them?

1. "S3 of the design brief" (line 48) — the source map for spec section rendering
2. "S3 fragment naming" (line 267) — fragment file naming convention
3. "S32" (line 278) — Dynamic Rewrite section
4. "per S3" (line 418) — session.md field inventory  
5. "S3 source map" (line 484) — spec section to source-node mapping
6. "S11 binding-layer order" (referenced in N-SPEC-CONSTRUCT.md)
7. "graph.json mode table" (line 284-285) — spawn soft/hard caps. This table does NOT exist in graph.json. The caps exist only in SKILL.md's MODE + FLAGS table (lines 98-100).

**Critical:** If the orchestrator follows the instruction "Compare to mode soft + hard caps from graph.json mode table" (line 284-285), it will fail because graph.json has no mode table. Where should the orchestrator actually read spawn caps from?

### 4b. Spawn Budget Tracking

1. SKILL.md lines 98-100 define hard caps: MINIMAL=3, STANDARD=7, DEEP=10. Soft caps are never explicitly given values — only the "mode soft + hard caps" phrase. What ARE the soft caps?
2. SKILL.md line 286: "On near-overflow (`spawn_count + planned_spawns >= soft_cap`): emit informational." Without soft cap values, this logic cannot execute.
3. `dry_run_pipeline.py` predicts spawn budget from static nodes only. D1/D2/D3 dynamic spawns are not accounted for. Is this an intentional limitation (static prediction only)?

### 4c. Ready-Set Edge Cases

The ready-set (F112, SKILL.md lines 236-244) has 3 conditions. Test these edge cases:
1. **All predecessors skipped:** if all nodes feeding N-AGGREGATION are masked (corrupted `active_branches`), the AND-join count = 0. Does N-AGGREGATION fire immediately with no inputs? Is there a defensive check?
2. **Empty ready-set with unfinished spawns:** a spawn node hangs. Does the orchestrator have a timeout/watchdog? Or does it wait forever?
3. **Skipped node propagation:** SKILL.md lines 241-244 say skipped nodes "propagate via the ready-set as if they had completed." How is this tracked — in memory only or in `topology-trace.md`? If the orchestrator crashes and resumes, does it re-derive skipped status correctly?

### 4d. Cap-Overflow Policy Coverage

Test every combination of mode + D-trigger + spawn budget:
1. **MINIMAL + D2 fire:** D2 requires 2 spawns (RANDOM-ENTRY + N-SPREADING re-fire). Base spawns at MINIMAL = N-CONSTRAINT-INVENTORY (1) + N-SPREADING (1) = 2. D2 adds 1 (N-SPREADING re-fire; RANDOM-ENTRY degraded to inline per SKILL.md line 360). Total = 3. Hard cap = 3. At-cap, not exceeding. Is this correct, or does the text "D2 always exceeds MINIMAL hard cap (3)" in SKILL.md line 359 indicate a bug in the threshold?
2. **DEEP + D1(5 gaps) + D2 + D3:** D1 adds up to 5 DOMAIN-TARGETED + 1 AGG re-fire = 6 spawns. Base = N-CONSTRAINT-INVENTORY (1) + 4 branches (4) + N-AGGREGATION (1) = 6. Total = 12 > hard cap 10. Overflow policy priority: D1 > D2 > D3. Is the cap-pressure exception for N-FORWARD-CHAIN-BATCH correctly prioritized?
3. **D1/D2 co-fire priority:** SKILL.md line 378 says "D1 takes priority." Does this mean D1 fires first and D2 re-evaluates after, or D2 is completely suppressed when D1 fires?

### 4e. Cross-Cutting Node Invocation

N-SCORE, N-DEFIXATION, N-REWRITE-EVALUATOR have no forward-chain edges. Verify:
1. N-SCORE: fires at step 6 of dispatch loop. "LLM-judged for creative-divergence nodes, deterministic for templating/transformation." How does the orchestrator know which category a node belongs to? Is there a data-driven mechanism or is it hardcoded?
2. N-REWRITE-EVALUATOR: fires at step 9 after EVERY node completion. D1/D2/D3 triggers are evaluated. Are triggers re-entrant safe? If D1 fires and adds DOMAIN-TARGETED nodes, does the next N-REWRITE-EVALUATOR invocation (after DOMAIN-TARGETED completes) correctly see the updated topology?
3. N-DEFIXATION: only fires via D2. If D2 never fires (SPREADING always above threshold), N-DEFIXATION is permanently dormant. Is this intentional?

---

## DIMENSION 5 — STATE MACHINE & RESUME

### 5a. State Machine Completeness

The state machine (SKILL.md lines 464-472) has 6 states. Audit:
1. Can the user abort from `AWAITING_CLARIFY`? (Phase 5 pause — currently no `[ABORT]` path defined.)
2. `AWAITING_REWORK_CONFIRM`: what if the user sends `[ABORT]`? SKILL.md lines 430-431 say the token is re-parsed under `AWAITING_GATE` rules, where `[ABORT]` → terminal `ABORTED`. Verify this two-hop path works.
3. Can the user send `[REWORK from phase 3] [CONFIRM-REWORK]` in a single message (pre-confirming)? The spec says the first top-level bracketed token at `AWAITING_GATE` wins — `[REWORK from phase 3]` transitions to `AWAITING_REWORK_CONFIRM` and emits a prompt. The `[CONFIRM-REWORK]` in the same message would be... ignored? Parsed as the next message? This multi-token-in-one-message case is undefined.

### 5b. Pause-Time Accounting

1. `pause_ts` is referenced in SKILL.md lines 404, 409, 412. Is it initialized in `session.md` template (written by `session-init.sh`)? If not, does `session_md_update.py --field pause_ts` work when the key doesn't exist yet?
2. DST transition: if pause is before a clock change and resume is after, does `(now - pause_ts)` produce a negative duration? Any guard?
3. Crash during pause: if the orchestrator crashes after setting `AWAITING_*` state, `pause_ts` is preserved on disk. The interval (possibly hours) is subtracted from phase budget. Is this correct? Does a very large subtraction cause underflow?

### 5c. session.md Corruption Recovery

1. `halt-session-md-unrecoverable` (SKILL.md line 169): v1.0 has only the `.bak` fallback. If BOTH `session.md` and `stages/session.md.bak` are unreadable, the session is permanently lost. The ledger (`grs-ledger.md`) is intact but cannot be used for reconstruction in v1.0. Is this acceptable for v1.0?
2. If `session.md` is corrupted (YAML parse fails), does the orchestrator detect this cleanly at resume and emit the structured halt envelope? Or does it crash with a raw Python/YAML traceback?

---

## DIMENSION 6 — PHASE 12 GATE & SIGNAL ROUTING

### 6a. Signal Parsing Completeness

The gate block (SKILL.md lines 500-529) defines 6 signal types. Audit:
1. `[REJECT items: 14.1]` — Section 14 special case routes to N-PRUNE re-execution, NOT N-REFINE-QUERY/N-FALSIFY. Is this divergence from the REJECT-items back-edge topology handled correctly by the orchestrator?
2. `[REJECT items: 14.1, APU-007]` — mixed section refs and APU refs in one REJECT signal. Undefined behavior. What SHOULD happen?
3. `[ADD: <text>]` — "text spans up to next bracketed token or EOM." What if the text itself contains `[` characters (e.g., "Add [APU-001] support")? Is greedy parsing safe?
4. Gate signal self-loop: after processing a REJECT/ADD/EDIT, the cycle counter increments, `spec-v(N+1).md` is emitted, and gate re-emits. Is there a maximum cycle limit to prevent infinite loops?

### 6b. Gate History & Cycle Counter

1. `gate_history` appends `{ts, signal, payload, cycle}` on each gate interaction (SKILL.md line 557). Is this append-only or does it replace?
2. Cycle counter: "REJECT / ADD / APPROVE WITH EDITS increment cycle counter" (line 559). Is the cycle counter used for anything other than fragment naming? Does it reset on `[REWORK]`? (SKILL.md line 549: "cycle counter CONTINUES from current value (NOT reset)")

### 6c. [APPROVE] Defensive Re-check

On `[APPROVE]` (SKILL.md lines 564-565): re-run V1a-V8 defensively. If V8 fails on retry: do NOT write `spec-final.md`; emit `[APPROVAL-BLOCKED]`; return state to `AWAITING_GATE`. If other V-checks deadlock: do NOT write `spec-final.md`; emit gate with deadlock tag. **Audit:** Does the orchestrator implement this retry-AND-NOT-WRITE logic correctly, or is there a path where a deadlocked V-check still permits `spec-final.md` to be written?

---

## DIMENSION 7 — V-CHECK BATTERY

### 7a. Re-route Map Completeness

| Check | Re-route Target | Max Re-routes |
|---|---|---|
| V1 | N-SPEC-CONSTRUCT (Phase 11) | 2 |
| V2 | N-SPEC-CONSTRUCT (Phase 11) | 2 |
| V3 | N-CONSTRAINT-INVENTORY (Phase 4) | 2 |
| V4 | Phase 6 with D2 forced | 2 |
| V5 | NO re-route (audit-only) | N/A |
| V6 | N-FALSIFY (Phase 11) | 2 |
| V7a | N-SPEC-CONSTRUCT (Phase 11) | 2 |
| V7b | N-SPEC-CONSTRUCT (Phase 11) | 2 |
| V8 | spec-chunk-write.sh (own path) | 2 |

Audit:
1. V1 and V2 BOTH re-route to N-SPEC-CONSTRUCT. If both fail simultaneously, does N-SPEC-CONSTRUCT execute once (satisfying both) or twice? The re-route counter is per-check — each independently counts its re-routes. Two executions of the same node may be wasteful but are they harmful?
2. V4 "Phase 6 with D2 forced" — does this forced D2 count against the D2 per-cycle limit of 2?
3. V5 has no re-route and "FAIL does not block sign-off." Verify this is implemented: V5 failure → gate warning only, user can still `[APPROVE]`.
4. V-check numbering: SKILL.md references "V1a" and "V1b" (lines 490, 510) but the verifications directory has only `v1_apu_coverage.py`. Were they merged? Is the naming discrepancy documented?

### 7b. Loop Protection

Max 2 re-routes per check. 3rd FAIL → `[VERIFICATION-DEADLOCK]`. Audit:
1. Is the re-route counter per-check AND per-session? (i.e., after 2 re-routes, the check permanently deadlocks for the session)
2. Deadlocked V1/V2/V3/V6/V7a/V7b block `[APPROVE]` (cannot finalize). Deadlocked V8 blocks finalize too. Can the user still `[REWORK]` or `[ABORT]` when deadlocked?
3. The confidence checkpoint policy (SKILL.md lines 643-648) describes a separate "phase confidence < 0.5 → reflexive re-route (max 2 per phase before DEADLOCK)." Is this re-route counter distinct from the V-check re-route counter?

---

## DIMENSION 8 — HALT STATE INVENTORY

### 8a. Classification Audit

The halt inventory (SKILL.md lines 135-173) lists 20 halt states. The "Logging discipline" note (lines 171-173) says only clarify-pause, gate-pause, and rework-confirm are informational — "All others terminate the pipeline."

Audit these specific entries for correct classification:
1. `halt-d2-replacement-limit` (line 161): D2 prose (lines 320-324) says "proceed with the best available N-SPREADING output, surface as gate warning." Proceeding = NOT terminating. But the halt inventory classifies it as terminating. **Contradiction.**
2. `halt-d3-reframe-limit` (line 162): D3 prose (lines 374-376) says "skip, log, add to open_questions_queue for human review at gate." Same pattern — sounds informational. **Contradiction.**
3. `halt-d1-aggregation-refire-skipped` (line 160): D1 prose says "abort D1 and log." Is aborting D1 (a sub-feature) the same as terminating the ENTIRE pipeline? Or does the pipeline continue minus D1?

### 8b. Reachability

For each halt state, trace the exact code path that triggers it. Flag any halt state that:
- References a script that doesn't exist
- Has a trigger condition that can never be satisfied
- Has contradictory triggering rules with another section of SKILL.md

### 8c. halt-time-budget-hardcap Edge Case

SKILL.md lines 132 and 168: Per-phase budget check (`actual > 3x rounded budget`). A long-running spawn node can blow past the hard cap mid-execution (the spawn runs in a subagent the orchestrator cannot preemptively kill). The halt triggers when the orchestrator checks the budget AFTER the node completes. **Audit:** Is this acceptable for v1.0? Document the limitation.

---

## DIMENSION 9 — TEST COVERAGE

### 9a. Script-to-Test Mapping

For every script, determine: does it have Python unit tests, shell integration tests, both, or neither?

| Script | Python Tests? | Shell Tests? | Gap? |
|---|---|---|---|
| `_yaml_io.py` | `test__yaml_io.py` (11 tests) | Indirect via session-init | |
| `ledger_append.py` | **NONE** | `test_ledger_append.sh` | **Critical gap**: zero Python unit tests for `_fragment_prefix()`, `_annotations_picked_up()`, `_digest_lines()` |
| `ledger_digest.py` | **NONE** | `test_ledger_digest.sh` | **Gap**: `split_entries()`, `emit()` are pure functions, untested in Python |
| `build_prompt.py` | Indirect via CLI test | `test_build_prompt.sh` | **Gap**: `--extra KEY=VALUE` path has ZERO tests |
| `session_md_update.py` | CLI test covers basic paths | `test_session_md_update.sh` | **Gap**: `--merge-yaml` with non-existent merge file not tested |
| All others | Various | Various | |

### 9b. Missing Edge Case Tests

1. **`apu_count=0`**: multiple scripts divide by `total_apus`. Test with zero APUs.
2. **`apu_count=30`**: the inline/spawn boundary for N-FORWARD-CHAIN-BATCH. Test exact boundary.
3. **Max APUs**: `dry_run_pipeline` goes to 50, but actual LLM could generate hundreds. Test large APU arrays.
4. **Cross-run seed with no prior sessions**: `seed_similarity` tests don't exercise first-time `cross_run_seed` initialization.
5. **V8: marker version mismatch** and **missing spec file**: neither path tested.
6. **V4: "pass when no branches active"** path not tested.
7. **Scale-mode cross-product**: no test verifies each `scale_gates` excludes correct nodes per mode. No MINIMAL+empty or DEEP+single-APU cross-product.

### 9c. Fixture Quality

1. All test fixtures are hand-crafted YAML/Markdown. No fixtures use actual LLM output formatting. Edge cases from LLM quirks (unusual whitespace, Markdown edge cases) are untested.
2. `tests/fixtures/specs/` has 6 spec files. Are there fixtures for: MINIMAL scale spec, DEEP scale spec, empty-APU spec, max-APU spec?

### 9d. Integration Test Gaps

No test exercises:
1. Full pipeline end-to-end (init → PRC1 → Phase 0..12 → export → gate)
2. Ready-set dispatch with scale-gated branch exclusion
3. D1/D2/D3 co-fire with spawn budget near cap
4. `--resume` from `AWAITING_CLARIFY` and `AWAITING_GATE`
5. Gate signal parsing for all 6 signal types
6. V-check re-route loop (2 re-routes then deadlock)
7. Edit-propagation routing with section-level diffs
8. `[REWORK from phase N]` + `[CONFIRM-REWORK]` cycle

For each: can it be tested without a real LLM? Which paths can use mock fragments?

---

## DIMENSION 10 — DOCUMENTATION & SPEC INTEGRITY

### 10a. Orphaned Content

1. `audit-prompt.md` at repo root — not referenced by any script, module, or SKILL.md. Contains stale numbers. Maintenance hazard.
2. `session.md.flags` field — written by `session-init.sh` but never explicitly consumed by any orchestrator logic. Audit-only field. Document this.
3. Any `hats.json` entries never referenced by any module?
4. Any scripts in the `scripts/` directory not listed in the Architecture section of SKILL.md (lines 46-47 missing `ledger_digest.py`, `build_prompt.py`, `session_md_update.py`, `finalize-spec.sh`, `compute_completeness.py`)?

### 10b. Version Consistency

1. v1.0.0 references: SKILL.md frontmatter, SKILL.md heading, graph.json — consistent?
2. v1.1 references: all explicitly marked "deferred to v1.1"? Any accidental v1.1 features wired in?
3. v2 references: `--improve` flag marked "v2-reserved; not implemented in v1." Any other v2 leakage?
4. Deferred threshold flags (strikethrough in SKILL.md lines 117-121): documented as Pass-3 F208. Are the hardcoded defaults consistent across all scripts?

### 10c. `session.md` Field Inventory

1. Every field written by `session-init.sh` — is it consumed somewhere in the orchestrator or a script?
2. `pause_ts` — used by orchestrator for pause-time accounting (SKILL.md lines 404, 409, 412). Is it initialized by `session-init.sh`? If not, does `session_md_update.py` handle writing to a previously-nonexistent key?
3. `created_ts` (line 128 of `session-init.sh`) — the only field with explicit YAML double-quote escaping (`\"`). Why? Is this fragile?
4. Any schema fields declared in `session-md-v1.schema.json` that are never written?

### 10d. Error Message Quality

Run `validate-graph.py` on intentionally broken graphs (missing node file, missing placeholder, duplicate node IDs, edge to non-existent node, malformed JSON). Are error messages:
- Actionable (reference specific node ID, file path, line number)?
- Consistent in format?
- Using the `PRC1.<n>:` prefix convention?

---

## PROCESS

Work through each dimension in order. For each finding, emit:

```
SEVERITY: <level>
FILE: <path>:<line>
FINDING: <one-line summary>
EVIDENCE: <what you observed — grep output, file content, logical deduction>
FIX: <concrete remediation — exact file edit, new logic, or removal>
```

After all 10 dimensions, produce a **priority-ranked punch list** of the top 15 issues by severity × likelihood of hitting in production. The first run of this skill on real input WILL encounter these.

**Dimensions summary:**
1. Topology & Edge Graph (AND-join, connectivity, phase numbering, dynamic templates, dead paths)
2. Module Prompt Quality (output mismatches, vague prompts, contradictions, data contracts, dangling refs)
3. Scripts & Security (injection, traversal, TOCTOU, atomicity, error handling, imports, ARG_MAX)
4. Orchestrator Coherence (undefined refs, spawn caps, ready-set edges, cap-overflow, cross-cutting nodes)
5. State Machine & Resume (state completeness, pause-time accounting, corruption recovery)
6. Phase 12 Gate & Signal Routing (signal parsing, gate history, approve re-check)
7. V-Check Battery (re-route map, loop protection, numbering, deadlock behavior)
8. Halt State Inventory (classification audit, reachability, contradictions)
9. Test Coverage (script-to-test mapping, edge cases, fixtures, integration gaps)
10. Documentation & Spec Integrity (orphaned content, version consistency, field inventory, error messages)
