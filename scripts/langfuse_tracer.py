#!/usr/bin/env python3
"""langfuse_tracer.py — optional Langfuse tracing for epiphany-spec sessions.

Subcommands (all exit 0 on soft failure so they never block the pipeline):

  init        --session-dir <path>
  node-span   --session-dir <path> --node-id <id> --phase <N> --cycle <N>
              --hat <name> --tier <tier> --exec-type <type>
              --score <float> --signals <json> --headline <text>
              --fragment <path> --provenance-tags <json> --annotations <json>
  finalize    --session-dir <path> --spec-path <path> --state <FINALIZED|ABORTED>

Config: ~/.claude/skills/epiphany-spec/langfuse.env
  EPIPHANY_LANGFUSE_PUBLIC_KEY=pk-lf-...
  EPIPHANY_LANGFUSE_SECRET_KEY=sk-lf-...
  EPIPHANY_LANGFUSE_HOST=http://localhost:3000
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, "/home/myuser/miniconda3/lib/python3.13/site-packages")

import warnings
warnings.filterwarnings("ignore")

# ── Config ────────────────────────────────────────────────────────────────────

_SKILL_DIR = Path(__file__).resolve().parents[1]
_CONFIG_FILE = _SKILL_DIR / "langfuse.env"
_STATE_FILENAME = ".langfuse_state.json"


def _load_config() -> dict[str, str]:
    cfg: dict[str, str] = {}
    if _CONFIG_FILE.exists():
        for line in _CONFIG_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            cfg[k.strip()] = v.strip()
    for key in ("EPIPHANY_LANGFUSE_PUBLIC_KEY", "EPIPHANY_LANGFUSE_SECRET_KEY",
                "EPIPHANY_LANGFUSE_HOST"):
        if key in os.environ:
            cfg[key] = os.environ[key]
    return cfg


def _get_langfuse(cfg: dict[str, str]):
    from langfuse import Langfuse  # type: ignore
    pk = cfg.get("EPIPHANY_LANGFUSE_PUBLIC_KEY", "")
    sk = cfg.get("EPIPHANY_LANGFUSE_SECRET_KEY", "")
    host = cfg.get("EPIPHANY_LANGFUSE_HOST", "http://localhost:3000")
    if not pk or not sk:
        return None
    return Langfuse(public_key=pk, secret_key=sk, host=host)


def _ingest(cfg: dict[str, str], batch: list) -> None:
    """Send events directly to the Langfuse ingestion API (for features the SDK
    doesn't expose, e.g. trace name and tags)."""
    import requests  # type: ignore
    pk = cfg.get("EPIPHANY_LANGFUSE_PUBLIC_KEY", "")
    sk = cfg.get("EPIPHANY_LANGFUSE_SECRET_KEY", "")
    host = cfg.get("EPIPHANY_LANGFUSE_HOST", "http://localhost:3000")
    auth = base64.b64encode(f"{pk}:{sk}".encode()).decode()
    requests.post(
        f"{host}/api/public/ingestion",
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
        json={"batch": batch},
        timeout=10,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _read_session(session_dir: Path) -> dict:
    sm = session_dir / "session.md"
    if not sm.exists():
        return {}
    try:
        import yaml  # type: ignore
        return yaml.safe_load(sm.read_text()) or {}
    except Exception:
        return {}


def _read_state(session_dir: Path) -> dict:
    f = session_dir / _STATE_FILENAME
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text())
    except Exception:
        return {}


def _write_state(session_dir: Path, state: dict) -> None:
    f = session_dir / _STATE_FILENAME
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.replace(f)


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_file_truncated(path: Path, max_chars: int = 8000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars:
            return text[:max_chars] + f"\n… [truncated at {max_chars} chars]"
        return text
    except Exception:
        return ""


def _exec_to_span_type(exec_type: str) -> str:
    if exec_type == "spawn":
        return "agent"
    return "span"


# ── Subcommands ───────────────────────────────────────────────────────────────

def cmd_init(session_dir: Path) -> None:
    cfg = _load_config()
    lf = _get_langfuse(cfg)
    if lf is None:
        print("[langfuse_tracer] no credentials — tracing disabled", file=sys.stderr)
        return

    from langfuse import Langfuse  # type: ignore
    from langfuse.types import TraceContext  # type: ignore

    sm = _read_session(session_dir)
    session_id = sm.get("session_id", str(session_dir.name))
    mode = sm.get("scale", "STANDARD")
    topic_slug = sm.get("topic_slug", "unknown")
    flags = sm.get("flags", "")
    active_branches = sm.get("active_branches", [])
    created_ts = sm.get("created_ts", "").strip('"\\')

    input_text = _read_file_truncated(session_dir / "input.md", max_chars=4000)
    trace_id = Langfuse.create_trace_id(seed=f"epiphany-spec-{session_id}")

    # Set trace name + tags via ingestion API (SDK v4 doesn't expose these).
    _ingest(cfg, [{
        "id": str(uuid.uuid4()),
        "type": "trace-create",
        "timestamp": _now_iso(),
        "body": {
            "id": trace_id,
            "name": f"epiphany-spec: {topic_slug[:60]}",
            "tags": ["skill:epiphany-spec", f"mode:{mode}"],
            "metadata": {
                "session_id": session_id,
                "mode": mode,
                "active_branches": active_branches,
                "flags": flags,
            },
        },
    }])

    span = lf.start_observation(
        trace_context=TraceContext(trace_id=trace_id),
        name="session-start",
        as_type="span",
        input={"session_id": session_id, "topic_slug": topic_slug, "mode": mode,
               "active_branches": active_branches, "flags": flags},
        metadata={"mode": mode, "topic_slug": topic_slug, "session_id": session_id,
                  "created_ts": created_ts},
    )
    span.set_trace_io(input={"topic": topic_slug, "mode": mode, "input": input_text})
    span.end()
    lf.flush()

    _write_state(session_dir, {
        "trace_id": trace_id,
        "session_id": session_id,
        "init_ts": _now_iso(),
        "node_count": 0,
        "trace_url": lf.get_trace_url(trace_id=trace_id),
    })
    print(f"[langfuse_tracer] trace created: {lf.get_trace_url(trace_id=trace_id)}")


def cmd_node_span(session_dir: Path, args: argparse.Namespace) -> None:
    cfg = _load_config()
    lf = _get_langfuse(cfg)
    if lf is None:
        return

    from langfuse.types import TraceContext  # type: ignore

    state = _read_state(session_dir)
    trace_id = state.get("trace_id")
    if not trace_id:
        print("[langfuse_tracer] no trace_id in state — skipping span", file=sys.stderr)
        return

    exec_type = args.exec_type
    hat = args.hat if args.hat and args.hat not in ("null", "none", "") else None

    try:
        score_val = float(args.score)
    except (TypeError, ValueError):
        score_val = None

    try:
        signals = json.loads(args.signals) if args.signals else {}
    except Exception:
        signals = {}

    try:
        provenance_tags = json.loads(args.provenance_tags) if args.provenance_tags else []
    except Exception:
        provenance_tags = []

    try:
        annotations = json.loads(args.annotations) if args.annotations else []
    except Exception:
        annotations = []

    # Read fragment — prefer ## output section; fall back to full content.
    fragment_content = ""
    if args.fragment:
        frag_path = (
            (session_dir / args.fragment)
            if not Path(args.fragment).is_absolute()
            else Path(args.fragment)
        )
        raw = _read_file_truncated(frag_path, max_chars=8000)
        # Try to extract from ## output section for a cleaner signal.
        if "## output" in raw:
            after = raw[raw.index("## output") + len("## output"):]
            fragment_content = after.strip() if after.strip() else raw
        else:
            fragment_content = raw

    output: dict = {"score": score_val, "headline": args.headline, "signals": signals}
    if fragment_content:
        output["content"] = fragment_content

    span = lf.start_observation(
        trace_context=TraceContext(trace_id=trace_id),
        name=args.node_id,
        as_type=_exec_to_span_type(exec_type),
        input={"node_id": args.node_id, "hat": hat, "exec_type": exec_type},
        output=output,
        metadata={
            "phase": args.phase,
            "cycle": args.cycle,
            "hat": hat,
            "tier": args.tier,
            "exec_type": exec_type,
            "signals": signals,
            "provenance_tags": provenance_tags,
            "annotations_picked_up": annotations,
        },
    )
    span.end()

    if score_val is not None and exec_type in ("inline", "spawn"):
        span.score_trace(name="node_score", value=score_val, comment=args.node_id)

    lf.flush()

    state["node_count"] = state.get("node_count", 0) + 1
    _write_state(session_dir, state)


def cmd_finalize(session_dir: Path, spec_path: str, state_name: str) -> None:
    cfg = _load_config()
    lf = _get_langfuse(cfg)
    if lf is None:
        return

    from langfuse.types import TraceContext  # type: ignore

    state = _read_state(session_dir)
    trace_id = state.get("trace_id")
    if not trace_id:
        print("[langfuse_tracer] no trace_id — skipping finalize", file=sys.stderr)
        return

    sm = _read_session(session_dir)
    topic_slug      = sm.get("topic_slug", "")
    final_version   = sm.get("final_version")
    node_count      = state.get("node_count", 0)
    apus            = sm.get("apus", [])
    convergent      = sm.get("convergent_nodes", [])
    spawn_count     = sm.get("spawn_count", 0)
    active_branches = sm.get("active_branches", [])
    open_questions  = sm.get("open_questions_queue", [])
    conflict_count  = len(sm.get("conflict_ledger", []))
    phase_actuals   = sm.get("phase_actuals", {})
    gate_history    = sm.get("gate_history", [])
    verification_log = sm.get("verification_log", [])

    # Read actual spec content — the primary artifact.
    spec_content = ""
    if spec_path:
        spec_content = _read_file_truncated(Path(spec_path), max_chars=8000)

    session_stats = {
        "apu_count":          len(apus),
        "convergent_node_count": len(convergent),
        "spawn_count":        spawn_count,
        "node_count":         node_count,
        "active_branches":    active_branches,
        "open_questions":     open_questions if isinstance(open_questions, list) else [open_questions],
        "conflict_count":     conflict_count,
        "gate_cycles":        len(gate_history),
    }
    if phase_actuals:
        session_stats["phase_actuals"] = phase_actuals

    output: dict = {
        "state": state_name,
        "topic_slug": topic_slug,
        **session_stats,
    }
    if spec_path:
        output["spec_path"] = spec_path
    if final_version is not None:
        output["final_version"] = final_version
    if spec_content:
        output["spec_content"] = spec_content

    span = lf.start_observation(
        trace_context=TraceContext(trace_id=trace_id),
        name="session-finalized" if state_name == "FINALIZED" else "session-aborted",
        as_type="span",
        input={"state": state_name},
        output=output,
        metadata={**session_stats, "state": state_name},
        level="DEFAULT" if state_name == "FINALIZED" else "WARNING",
    )
    span.set_trace_io(output=output)
    span.end()

    # Scores.
    if isinstance(verification_log, list) and verification_log:
        pass_count = sum(1 for v in verification_log if isinstance(v, dict) and v.get("result") == "pass")
        total = len(verification_log)
        if total > 0:
            span.score_trace(
                name="verification_pass_rate",
                value=round(pass_count / total, 3),
                comment=f"{pass_count}/{total} checks passed",
            )

    if state_name == "FINALIZED":
        span.score_trace(name="finalized", value=1.0, comment="spec-final.md written")

    lf.flush()
    print(f"[langfuse_tracer] trace finalized: {state.get('trace_url', trace_id)}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(description="Langfuse tracer for epiphany-spec")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--session-dir", required=True, type=Path)

    p_ns = sub.add_parser("node-span")
    p_ns.add_argument("--session-dir",      required=True, type=Path)
    p_ns.add_argument("--node-id",          required=True)
    p_ns.add_argument("--phase",            required=True)
    p_ns.add_argument("--cycle",            required=True)
    p_ns.add_argument("--hat",              required=True)
    p_ns.add_argument("--tier",             required=True)
    p_ns.add_argument("--exec-type",        required=True)
    p_ns.add_argument("--score",            default="")
    p_ns.add_argument("--signals",          default="{}")
    p_ns.add_argument("--headline",         default="")
    p_ns.add_argument("--fragment",         default="")
    p_ns.add_argument("--provenance-tags",  default="[]")
    p_ns.add_argument("--annotations",      default="[]")

    p_fin = sub.add_parser("finalize")
    p_fin.add_argument("--session-dir", required=True, type=Path)
    p_fin.add_argument("--spec-path",   default="")
    p_fin.add_argument("--state",       default="FINALIZED")

    args = p.parse_args()

    try:
        if args.cmd == "init":
            cmd_init(args.session_dir)
        elif args.cmd == "node-span":
            cmd_node_span(args.session_dir, args)
        elif args.cmd == "finalize":
            cmd_finalize(args.session_dir, args.spec_path, args.state)
    except Exception as exc:
        print(f"[langfuse_tracer] error (non-fatal): {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
