"""Output capture and parsing for Claude Code runs."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


def parse_output(stdout: str) -> Dict[str, Any]:
    """Parse stream-json output into structured data."""
    if not stdout:
        return {"messages": []}
    messages = []
    for line in stdout.strip().split('\n'):
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return {"messages": messages}


def extract_events(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Extract events (tool calls, files, etc.) from parsed output."""
    events = {
        "tool_calls": [], "files_read": [], "files_created": [],
        "files_modified": [], "commands_run": [],
        "duration_seconds": None, "num_turns": None,
    }

    for msg in parsed.get("messages", []):
        if msg.get("type") == "result":
            events["duration_seconds"] = msg.get("duration_ms", 0) / 1000
            events["num_turns"] = msg.get("num_turns")

        if msg.get("type") == "assistant":
            for item in msg.get("message", {}).get("content", []):
                if item.get("type") == "tool_use":
                    tool, inp = item.get("name", ""), item.get("input", {})
                    events["tool_calls"].append({"tool": tool, "input": inp})
                    path = inp.get("file_path", "")
                    if tool == "Read" and path:
                        events["files_read"].append(path)
                    elif tool == "Write" and path:
                        events["files_created"].append(path)
                    elif tool == "Edit" and path:
                        events["files_modified"].append(path)
                    elif tool == "Bash" and inp.get("command"):
                        events["commands_run"].append(inp["command"])
    return events


def save_events(events: Dict[str, Any], output_dir: Path, name: str) -> Path:
    """Save events to JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = name.replace(" ", "_").replace("/", "_").lower()
    path = output_dir / f"{safe}_{ts}.json"
    path.write_text(json.dumps(events, indent=2))
    return path


def summarize(events: Dict[str, Any]) -> str:
    """One-line summary of events."""
    parts = []
    if events.get("duration_seconds"):
        parts.append(f"{events['duration_seconds']:.0f}s")
    if events.get("num_turns"):
        parts.append(f"{events['num_turns']} turns")
    if events.get("tool_calls"):
        tools = {}
        for tc in events["tool_calls"]:
            tools[tc["tool"]] = tools.get(tc["tool"], 0) + 1
        parts.append(" ".join(f"{k}:{v}" for k, v in tools.items()))
    return " | ".join(parts) if parts else "no data"


# Validation helpers
def did_read(events: Dict, filename: str) -> bool:
    return any(filename in f for f in events.get("files_read", []))

def did_create(events: Dict, filename: str) -> bool:
    return any(filename in f for f in events.get("files_created", []))

def tool_count(events: Dict, tool_name: str) -> int:
    return sum(1 for tc in events.get("tool_calls", []) if tc["tool"] == tool_name)
