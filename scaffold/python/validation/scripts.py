"""Skill script usage validation.

Tracks which skill scripts Claude used during a task.
This is informational - doesn't fail, just records patterns.
"""

from pathlib import Path

# Known skill scripts by language
PY_SCRIPTS = [
    "query_traces.py",
    "generate_datasets.py",
    "query_datasets.py",
    "upload_evaluators.py",
]

TS_SCRIPTS = [
    "query_traces.ts",
    "generate_datasets.ts",
    "query_datasets.ts",
    "upload_evaluators.ts",
]


def validate_skill_scripts(
    test_dir: Path,
    outputs: dict,
    events: dict | None = None,
    py_scripts: list[str] | None = None,
    ts_scripts: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Track which skill scripts Claude used (Python vs TypeScript).

    This validator doesn't fail - it just records usage patterns for analysis.
    Key insight: Did Claude use the correct language script for each task?
    - When working on Python agent: should use .py scripts
    - When working on TypeScript agent: should use .ts scripts

    Args:
        test_dir: Test working directory (unused but matches signature)
        outputs: Outputs dict (stores script usage for later analysis)
        events: Events dict containing commands_run and files_read
        py_scripts: Python script names to look for
        ts_scripts: TypeScript script names to look for

    Returns:
        (passed, failed) lists - never fails, only passes
    """
    passed, failed = [], []
    events = events or {}
    py_scripts = py_scripts or PY_SCRIPTS
    ts_scripts = ts_scripts or TS_SCRIPTS

    commands = " ".join(events.get("commands_run", [])).lower()
    files_read = " ".join(events.get("files_read", [])).lower()
    all_activity = commands + " " + files_read

    # Count script usage
    py_used = [s for s in py_scripts if s.lower() in all_activity]
    ts_used = [s for s in ts_scripts if s.lower() in all_activity]

    # Report findings
    if py_used:
        passed.append(f"Scripts: {len(py_used)} Python scripts used ({', '.join(py_used)})")
    if ts_used:
        passed.append(f"Scripts: {len(ts_used)} TypeScript scripts used ({', '.join(ts_used)})")

    if not py_used and not ts_used:
        passed.append("Scripts: no skill scripts used (Claude wrote from scratch)")

    # Check for language mixing - this is informational, not a failure
    if py_used and ts_used:
        passed.append("Scripts: mixed Python and TypeScript scripts")
    elif py_used and not ts_used:
        passed.append("Scripts: Python-only approach")
    elif ts_used and not py_used:
        passed.append("Scripts: TypeScript-only approach")

    # Store in outputs for later analysis
    if outputs is not None:
        outputs["py_scripts_used"] = py_used
        outputs["ts_scripts_used"] = ts_used

    return passed, failed
