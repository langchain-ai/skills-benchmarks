"""Skill tool usage validation.

Tracks which skill tools (langsmith CLI commands) Claude used during a task.
This is informational - doesn't fail, just records patterns.
"""

# Known langsmith CLI subcommands
CLI_COMMANDS = [
    "langsmith trace",
    "langsmith run",
    "langsmith dataset",
    "langsmith evaluator",
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
