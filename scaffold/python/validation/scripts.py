"""Skill tool usage validation.

Tracks which skill tools (langsmith CLI commands) Claude used during a task.
This is informational - doesn't fail, just records patterns.
"""

# Known langsmith CLI subcommands
CLI_COMMANDS = [
    "langsmith trace",
    "langsmith run",
    "langsmith dataset",
    "langsmith example",
    "langsmith evaluator",
    "langsmith experiment",
    "langsmith thread",
    "langsmith project",
]


def check_skill_scripts(
    outputs: dict,
    events: dict | None = None,
    cli_commands: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Track which langsmith CLI commands Claude used.

    This validator doesn't fail - it just records usage patterns for analysis.

    Args:
        outputs: Outputs dict (stores CLI usage for later analysis)
        events: Events dict containing commands_run and files_read
        cli_commands: CLI command patterns to look for

    Returns:
        (passed, failed) lists - never fails, only passes
    """
    passed, failed = [], []
    events = events or {}
    cli_commands = cli_commands or CLI_COMMANDS

    commands = " ".join(events.get("commands_run", [])).lower()
    files_read = " ".join(events.get("files_read", [])).lower()
    all_activity = commands + " " + files_read

    # Count CLI command usage
    cli_used = [c for c in cli_commands if c.lower() in all_activity]

    # Report findings
    if cli_used:
        passed.append(f"CLI: {len(cli_used)} langsmith commands used ({', '.join(cli_used)})")
    else:
        passed.append("CLI: no langsmith CLI commands used (Claude wrote from scratch)")

    # Store in outputs for later analysis
    if outputs is not None:
        outputs["cli_commands_used"] = cli_used

    return passed, failed


def check_reference_consulted(
    events: dict | None,
    reference_filename: str,
    *,
    required: bool = True,
) -> tuple[list[str], list[str]]:
    """Check that Claude read a specific reference file under a skill's references/ dir.

    Used by per-framework tracing tasks to verify that the langsmith-trace skill's
    routing table directed Claude to the right reference (e.g., references/autogen.md
    when given an AutoGen task).

    Args:
        events: Events dict containing files_read (list of paths Claude opened).
        reference_filename: Bare filename, e.g. "autogen.md". Matched against any
            files_read entry ending in "references/<reference_filename>".
        required: If True, missing read is a failure. If False, only informational.

    Returns:
        (passed, failed) lists.
    """
    events = events or {}
    files_read = events.get("files_read", []) or []
    needle = f"references/{reference_filename}".lower()

    hit = any(needle in path.lower() for path in files_read)

    if hit:
        return [f"Consulted reference: {reference_filename}"], []
    if required:
        return [], [f"Did NOT consult expected reference: {reference_filename}"]
    return [f"Note: did not consult {reference_filename}"], []
