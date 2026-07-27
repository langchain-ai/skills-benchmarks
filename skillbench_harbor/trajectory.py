"""Extract agent telemetry from a Harbor trial directory.

Harbor stores each trial under ``jobs/<run>/<task>__<id>/`` with:
  - ``result.json``            uniform per-trial metrics (all agents)
  - ``agent/trajectory.json``  Harbor's normalized trajectory (codex, claude-code)
  - ``agent/<agent>.txt``      the agent's raw stdout (agent-specific format)

Core metrics (tokens, cost, duration, model) come from ``result.json`` and are
agent-agnostic. Turn count comes from the trajectory's ``final_metrics``. Tool
calls and skill invocations are only in the raw ``<agent>.txt`` stream, whose
shape is agent-specific, so those are parsed per agent.

All reads are read-only and scoped to the given trial directory.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

# Skill directories each agent copies treatment skills into.
_SKILL_DIR_MARKERS = (".claude/skills/", ".agents/skills/", "/skills/")


def _empty_events() -> dict[str, Any]:
    return {
        "agent": None,
        "model": None,
        "num_turns": None,
        "tool_calls": [],
        "commands_run": [],
        "files_read": [],
        "files_created": [],
        "files_modified": [],
        "skills_invoked": [],
        "duration_seconds": None,
        "total_cost_usd": None,
        "usage": None,
    }


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _iter_jsonl(path: Path):
    try:
        text = path.read_text()
    except (FileNotFoundError, OSError):
        return
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def _skill_from_path(path: str) -> str | None:
    """Return the skill name if a path points inside a skills directory."""
    for marker in _SKILL_DIR_MARKERS:
        if marker in path:
            rest = path.split(marker, 1)[1].strip("/")
            if rest:
                return rest.split("/")[0]
    return None


def find_trial_dir(job_dir: Path) -> Path | None:
    """Resolve the trial directory holding result.json under a sweep job dir.

    ``job_dir`` may be the run dir (``jobs/<run>/``) or already the trial dir.
    """
    if (job_dir / "result.json").is_file() and (job_dir / "agent").is_dir():
        return job_dir
    candidates = sorted(job_dir.glob("*/result.json"))
    if candidates:
        return candidates[0].parent
    return None


def _core_metrics(events: dict[str, Any], trial_dir: Path) -> None:
    """Fill agent-agnostic metrics from result.json."""
    result = _read_json(trial_dir / "result.json")
    if not isinstance(result, dict):
        return

    info = result.get("agent_info") or {}
    events["agent"] = info.get("name")
    model_info = info.get("model_info") or {}
    events["model"] = model_info.get("name")

    ar = result.get("agent_result") or {}
    events["total_cost_usd"] = ar.get("cost_usd")
    if any(k in ar for k in ("n_input_tokens", "n_output_tokens", "n_cache_tokens")):
        events["usage"] = {
            "input_tokens": ar.get("n_input_tokens", 0),
            "output_tokens": ar.get("n_output_tokens", 0),
            "cache_read_input_tokens": ar.get("n_cache_tokens", 0),
        }

    ax = result.get("agent_execution") or {}
    events["duration_seconds"] = _duration(ax.get("started_at"), ax.get("finished_at"))


def _duration(started: str | None, finished: str | None) -> float | None:
    if not started or not finished:
        return None
    try:
        s = datetime.fromisoformat(started.replace("Z", "+00:00"))
        f = datetime.fromisoformat(finished.replace("Z", "+00:00"))
        return (f - s).total_seconds()
    except (ValueError, AttributeError):
        return None


def _num_turns(trial_dir: Path) -> int | None:
    traj = _read_json(trial_dir / "agent" / "trajectory.json")
    if isinstance(traj, dict):
        fm = traj.get("final_metrics") or {}
        if fm.get("total_steps") is not None:
            return fm["total_steps"]
    return None


def _add_skill(events: dict[str, Any], name: str | None) -> None:
    if name and name not in events["skills_invoked"]:
        events["skills_invoked"].append(name)


def _parse_claude_code(events: dict[str, Any], raw: Path) -> None:
    """Parse claude-code stream-json (one JSON object per line)."""
    for msg in _iter_jsonl(raw):
        if not isinstance(msg, dict):
            continue
        if msg.get("type") == "result" and events["num_turns"] is None:
            events["num_turns"] = msg.get("num_turns")
        if msg.get("type") != "assistant":
            continue
        for item in msg.get("message", {}).get("content", []):
            if not isinstance(item, dict) or item.get("type") != "tool_use":
                continue
            tool, inp = item.get("name", ""), item.get("input", {}) or {}
            events["tool_calls"].append({"tool": tool, "input": inp})
            path = inp.get("file_path", "")
            if tool == "Read" and path:
                events["files_read"].append(path)
                _add_skill(events, _skill_from_path(path))
            elif tool == "Write" and path:
                events["files_created"].append(path)
            elif tool == "Edit" and path:
                events["files_modified"].append(path)
            elif tool == "Bash" and inp.get("command"):
                events["commands_run"].append(inp["command"])
            elif tool == "Skill" and inp.get("skill"):
                _add_skill(events, inp["skill"])


def _parse_codex(events: dict[str, Any], raw: Path) -> None:
    """Parse codex JSON-lines output (item.started/completed, turn.completed)."""
    for msg in _iter_jsonl(raw):
        if not isinstance(msg, dict):
            continue
        if msg.get("type") != "item.completed":
            continue
        item = msg.get("item", {}) or {}
        if item.get("type") == "command_execution":
            command = item.get("command", "")
            events["tool_calls"].append({"tool": "command_execution", "input": command})
            if command:
                events["commands_run"].append(command)
                _add_skill(events, _skill_from_path(command))


def _parse_langgraph(events: dict[str, Any], agent_dir: Path) -> None:
    """Best-effort parse of deepagents/langgraph output.

    deepagents does not emit a structured per-tool trajectory here, so tool and
    skill detection is a text scan over the run output; usage comes from
    summary.json when result.json lacked it.
    """
    summary = _read_json(agent_dir / "summary.json")
    if isinstance(summary, dict) and events["usage"] is None:
        usage = summary.get("usage")
        if isinstance(usage, dict):
            events["usage"] = {
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "cache_read_input_tokens": usage.get("cache_read_tokens", 0),
            }
    for candidate in ("langgraph.txt", "langgraph-run.log"):
        text = ""
        try:
            text = (agent_dir / candidate).read_text()
        except (FileNotFoundError, OSError):
            continue
        for marker in _SKILL_DIR_MARKERS:
            idx = 0
            while (idx := text.find(marker, idx)) != -1:
                _add_skill(events, _skill_from_path(text[idx : idx + 200]))
                idx += len(marker)


def extract_trial_events(job_dir: Path) -> dict[str, Any]:
    """Extract telemetry for one trial. ``job_dir`` = sweep run or trial dir."""
    events = _empty_events()
    trial_dir = find_trial_dir(Path(job_dir))
    if trial_dir is None:
        return events

    _core_metrics(events, trial_dir)
    events["num_turns"] = _num_turns(trial_dir)

    agent = (events["agent"] or "").lower()
    agent_dir = trial_dir / "agent"
    if agent == "claude-code":
        _parse_claude_code(events, agent_dir / "claude-code.txt")
    elif agent == "codex":
        _parse_codex(events, agent_dir / "codex.txt")
    elif agent == "langgraph":
        _parse_langgraph(events, agent_dir)

    return events
