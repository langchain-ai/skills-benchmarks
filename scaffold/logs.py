#!/usr/bin/env python3
"""Generate human-readable test reports."""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional


def find_recent_events(events_dir: Path, hours: int = 24) -> list[Path]:
    cutoff = datetime.now().timestamp() - (hours * 3600)
    return sorted([f for f in events_dir.glob("*.json") if f.stat().st_mtime > cutoff],
                  key=lambda x: x.stat().st_mtime, reverse=True)


def summarize_event(event_file: Path) -> dict:
    data = json.loads(event_file.read_text())
    tool_counts = {}
    for tc in data.get("tool_calls", []):
        tool_counts[tc["tool"]] = tool_counts.get(tc["tool"], 0) + 1
    return {
        "name": event_file.stem.rsplit("_", 2)[0],
        "file": event_file.name,
        "duration": data.get("duration_seconds"),
        "turns": data.get("num_turns"),
        "tool_counts": tool_counts,
        "files_read": [f.split("/")[-1] for f in data.get("files_read", [])],
        "files_created": [f.split("/")[-1] for f in data.get("files_created", [])],
        "commands": data.get("commands_run", [])[:5],
    }


def print_event_summary(s: dict) -> None:
    print(f"\n{'='*60}\nTEST: {s['name']}\n{'='*60}")
    print(f"File: {s['file']}")
    if s['duration']:
        print(f"Duration: {s['duration']:.0f}s")
    if s['turns']:
        print(f"Turns: {s['turns']}")
    if s['tool_counts']:
        print(f"Tools: {', '.join(f'{k}:{v}' for k, v in sorted(s['tool_counts'].items()))}")
    if s['files_read']:
        print(f"Read: {', '.join(s['files_read'][:10])}")
    if s['files_created']:
        print(f"Created: {', '.join(s['files_created'])}")
    if s['commands']:
        print("Commands:")
        for cmd in s['commands']:
            print(f"  $ {cmd[:80]}...")


def generate_report(events_dir: Path, hours: int = 24, test_filter: Optional[str] = None) -> None:
    files = find_recent_events(events_dir, hours)
    if test_filter:
        files = [f for f in files if test_filter.lower() in f.name.lower()]
    if not files:
        print(f"No events found in last {hours} hours")
        return

    print(f"SKILL BENCHMARK REPORT\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\nEvents: {len(files)}")
    for f in files:
        try:
            print_event_summary(summarize_event(f))
        except Exception as e:
            print(f"\nError reading {f.name}: {e}")
    print(f"\n{'='*60}\nEND OF REPORT\n{'='*60}")


def compare_runs(events_dir: Path, pattern: str) -> None:
    files = list(events_dir.glob(f"*{pattern}*.json"))
    if not files:
        print(f"No files matching '{pattern}'")
        return

    print(f"COMPARING {len(files)} RUNS matching '{pattern}'\n{'='*60}")
    summaries = [summarize_event(f) for f in sorted(files) if f.exists()]
    print(f"{'Name':<30} {'Duration':<10} {'Tools':<20} {'Created':<20}\n{'-'*80}")
    for s in summaries:
        tools = ",".join(f"{k}:{v}" for k, v in list(s['tool_counts'].items())[:3])
        created = ",".join(s['files_created'][:2])
        dur = f"{s['duration']:.0f}s" if s['duration'] else "?"
        print(f"{s['name']:<30} {dur:<10} {tools:<20} {created:<20}")


def show_test_detail(events_dir: Path, test_name: str) -> None:
    matches = list(events_dir.glob(f"*{test_name}*.json"))
    if not matches:
        print(f"No events matching '{test_name}'")
        return

    f = max(matches, key=lambda x: x.stat().st_mtime)
    data = json.loads(f.read_text())

    print(f"DETAILED VIEW: {f.name}\n{'='*60}")
    print(f"Duration: {data.get('duration_seconds', 0):.1f}s\nTurns: {data.get('num_turns', 'N/A')}")
    print(f"\n--- TOOL CALLS ({len(data.get('tool_calls', []))}) ---")

    for i, tc in enumerate(data.get('tool_calls', [])):
        tool, inp = tc['tool'], tc.get('input', {})
        path = inp.get('file_path', '').split('/')[-1]
        if tool == 'Read':
            print(f"{i+1}. Read: {path}")
        elif tool == 'Write':
            print(f"{i+1}. Write: {path}\n    Preview: {inp.get('content', '')[:100].replace(chr(10), ' ')}...")
        elif tool == 'Bash':
            print(f"{i+1}. Bash: {inp.get('command', '')[:80]}")
        elif tool == 'Edit':
            print(f"{i+1}. Edit: {path}")
        else:
            print(f"{i+1}. {tool}")

    print("\n--- FILES READ ---")
    for f in data.get('files_read', []):
        print(f"  {f.split('/')[-1]}")
    print("\n--- FILES CREATED ---")
    for f in data.get('files_created', []):
        print(f"  {f.split('/')[-1]}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="View test reports")
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument("--filter", type=str)
    parser.add_argument("--compare", type=str)
    parser.add_argument("--detail", type=str)
    args = parser.parse_args()

    events_dir = Path(__file__).parent.parent / "logs" / "events"
    if args.compare:
        compare_runs(events_dir, args.compare)
    elif args.detail:
        show_test_detail(events_dir, args.detail)
    else:
        generate_report(events_dir, args.hours, args.filter)
