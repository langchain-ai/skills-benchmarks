"""Experiment-based logging and summary generation."""

import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable

PROJECT_ROOT = Path(__file__).parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"

# Regex to strip ANSI escape codes
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    return ANSI_ESCAPE.sub('', text)


# =============================================================================
# OUTPUT PARSING
# =============================================================================

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
        "files_modified": [], "commands_run": [], "skills_invoked": [],
        "duration_seconds": None, "num_turns": None,
    }

    # Map tool_use_id -> index in tool_calls list for matching outputs
    tool_id_to_index = {}

    for msg in parsed.get("messages", []):
        if msg.get("type") == "result":
            events["duration_seconds"] = msg.get("duration_ms", 0) / 1000
            events["num_turns"] = msg.get("num_turns")

        if msg.get("type") == "assistant":
            for item in msg.get("message", {}).get("content", []):
                if item.get("type") == "tool_use":
                    tool, inp = item.get("name", ""), item.get("input", {})
                    tool_id = item.get("id")
                    tool_call = {"tool": tool, "input": inp}
                    if tool_id:
                        tool_id_to_index[tool_id] = len(events["tool_calls"])
                    events["tool_calls"].append(tool_call)
                    path = inp.get("file_path", "")
                    if tool == "Read" and path:
                        events["files_read"].append(path)
                    elif tool == "Write" and path:
                        events["files_created"].append(path)
                    elif tool == "Edit" and path:
                        events["files_modified"].append(path)
                    elif tool == "Bash" and inp.get("command"):
                        events["commands_run"].append(inp["command"])
                    elif tool == "Skill" and inp.get("skill"):
                        events["skills_invoked"].append(inp["skill"])

        # Capture tool results and match to their tool_use calls
        if msg.get("type") == "user":
            for item in msg.get("message", {}).get("content", []):
                if item.get("type") == "tool_result":
                    tool_use_id = item.get("tool_use_id")
                    if tool_use_id and tool_use_id in tool_id_to_index:
                        idx = tool_id_to_index[tool_use_id]
                        # Extract output content
                        content = item.get("content", "")
                        if isinstance(content, list):
                            # Content can be a list of text blocks
                            content = " ".join(
                                c.get("text", str(c)) if isinstance(c, dict) else str(c)
                                for c in content
                            )
                        events["tool_calls"][idx]["output"] = content

    return events


# =============================================================================
# TREATMENT RESULT
# =============================================================================

@dataclass
class TreatmentResult:
    """Result from a single treatment run."""
    name: str
    passed: bool
    checks_passed: List[str]
    checks_failed: List[str]
    events_summary: Dict[str, Any] = field(default_factory=dict)

    def has_check(self, pattern: str) -> bool:
        """Check if any passed check contains pattern."""
        return any(pattern in c for c in self.checks_passed)

    def has_failed_check(self, pattern: str) -> bool:
        """Check if any failed check contains pattern."""
        return any(pattern in c for c in self.checks_failed)

    @property
    def turns(self) -> Optional[int]:
        return self.events_summary.get("num_turns")

    @property
    def duration(self) -> Optional[float]:
        return self.events_summary.get("duration_seconds")

    @property
    def tool_calls(self) -> Optional[int]:
        return self.events_summary.get("tool_calls")


# =============================================================================
# REPORT COLUMNS
# =============================================================================

@dataclass
class ReportColumn:
    """Defines a column in the results table."""
    name: str
    extract: Callable[[TreatmentResult], str]  # Single run -> display value
    aggregate: Callable[[List[TreatmentResult]], str] = None  # Multiple runs -> display value

    def get_value(self, result: TreatmentResult) -> str:
        return self.extract(result)

    def get_aggregate(self, runs: List[TreatmentResult]) -> str:
        if self.aggregate:
            return self.aggregate(runs)
        return self.extract(runs[0]) if runs else "N/A"


def bool_column(name: str, pattern: str) -> ReportColumn:
    """Column that checks if pattern exists in passed checks."""
    return ReportColumn(
        name=name,
        extract=lambda r: "Yes" if r.has_check(pattern) else "No",
        aggregate=lambda runs: f"{sum(1 for r in runs if r.has_check(pattern))}/{len(runs)}",
    )


def quality_column(name: str = "Quality") -> ReportColumn:
    """Column for output quality ([GOOD] vs [LOW])."""
    def extract(r):
        for c in r.checks_passed:
            if "[GOOD]" in c:
                return "Good"
            if "[LOW]" in c:
                return "Low"
        return "N/A"

    def aggregate(runs):
        good = sum(1 for r in runs if any("[GOOD]" in c for c in r.checks_passed))
        return f"{good}/{len(runs)}"

    return ReportColumn(name=name, extract=extract, aggregate=aggregate)


def default_columns() -> List[ReportColumn]:
    """Standard columns: Pass, Turns, Duration, Tools."""
    return [
        ReportColumn(
            name="Pass",
            extract=lambda r: "PASS" if r.passed else "FAIL",
            aggregate=lambda runs: f"{sum(1 for r in runs if r.passed)}/{len(runs)}",
        ),
        ReportColumn(
            name="Turns",
            extract=lambda r: str(r.turns) if r.turns else "N/A",
            aggregate=lambda runs: _avg([r.turns for r in runs if r.turns], "{:.0f}"),
        ),
        ReportColumn(
            name="Duration",
            extract=lambda r: f"{r.duration:.0f}s" if r.duration else "N/A",
            aggregate=lambda runs: _avg([r.duration for r in runs if r.duration], "{:.0f}s"),
        ),
        ReportColumn(
            name="Tools",
            extract=lambda r: str(r.tool_calls) if r.tool_calls else "N/A",
            aggregate=lambda runs: _avg([r.tool_calls for r in runs if r.tool_calls], "{:.0f}"),
        ),
    ]


def _avg(values: List, fmt: str = "{:.1f}") -> str:
    """Calculate average and format, or return N/A."""
    values = [v for v in values if v is not None]
    if not values:
        return "N/A"
    return fmt.format(sum(values) / len(values))


# =============================================================================
# EXPERIMENT LOGGER
# =============================================================================

class ExperimentLogger:
    """Manages logging for a single experiment run."""

    def __init__(self, experiment_name: str = None, columns: List[ReportColumn] = None):
        """Create experiment logger.

        Args:
            experiment_name: Name for this experiment
            columns: Custom columns for reporting (in addition to defaults)
        """
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.name = experiment_name or f"experiment_{self.timestamp}"
        self.experiment_id = f"{self.name}_{self.timestamp}"
        self.base_dir = LOGS_DIR / "experiments" / self.experiment_id

        # Create subdirectories
        self.code_dir = self.base_dir / "code"
        self.docker_dir = self.base_dir / "docker"
        self.events_dir = self.base_dir / "events"
        self.reports_dir = self.base_dir / "reports"
        self.raw_dir = self.base_dir / "raw"

        for d in [self.code_dir, self.docker_dir, self.events_dir,
                  self.reports_dir, self.raw_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.columns = columns or []
        self.results: Dict[str, List[TreatmentResult]] = {}
        self.metadata: Dict[str, Any] = {
            "experiment_id": self.experiment_id,
            "started_at": datetime.now().isoformat(),
            "treatments": [],
        }

    def add_result(self, treatment_name: str, result: TreatmentResult):
        """Add a treatment result."""
        if treatment_name not in self.results:
            self.results[treatment_name] = []
            self.metadata["treatments"].append(treatment_name)
        self.results[treatment_name].append(result)

    def _get_all_columns(self) -> List[ReportColumn]:
        """Get all columns: custom first, then defaults."""
        defaults = default_columns()
        pass_col = defaults[0]
        metric_cols = defaults[1:]
        return [pass_col] + self.columns + metric_cols

    def generate_summary(self) -> str:
        """Generate markdown summary of experiment results."""
        lines = []
        lines.append("# Experiment Results Summary\n")
        lines.append(f"**Experiment ID:** `{self.experiment_id}`\n")
        lines.append(f"**Started:** {self.metadata['started_at']}\n")
        lines.append(f"**Completed:** {datetime.now().isoformat()}\n")
        lines.append("")

        columns = self._get_all_columns()
        has_reps = any(len(runs) > 1 for runs in self.results.values())

        col_names = ["Treatment"] + [c.name for c in columns]
        header = "| " + " | ".join(col_names) + " |"
        separator = "|" + "|".join("-" * (len(name) + 2) for name in col_names) + "|"

        if has_reps:
            lines.append("## Results (with Repetitions)\n")
        else:
            lines.append("## Results\n")

        lines.append(header)
        lines.append(separator)

        for name, runs in self.results.items():
            if has_reps:
                values = [c.get_aggregate(runs) for c in columns]
            else:
                values = [c.get_value(runs[0]) for c in columns]
            lines.append(f"| {name} | " + " | ".join(values) + " |")

        lines.append("")

        total_runs = sum(len(runs) for runs in self.results.values())
        total_passed = sum(sum(1 for r in runs if r.passed) for runs in self.results.values())

        lines.append("## Summary\n")
        lines.append(f"- **Total Runs:** {total_runs}")
        lines.append(f"- **Pass Rate:** {total_passed}/{total_runs} ({100*total_passed//total_runs if total_runs else 0}%)")
        lines.append("")

        failed_runs = [
            (name, r) for name, runs in self.results.items()
            for r in runs if not r.passed
        ]
        if failed_runs:
            lines.append("## Failed Runs\n")
            for name, r in failed_runs[:10]:
                lines.append(f"- **{name}:** {', '.join(r.checks_failed[:2])}")
            if len(failed_runs) > 10:
                lines.append(f"- ... and {len(failed_runs) - 10} more")

        return "\n".join(lines)

    def finalize(self):
        """Generate and save final summary."""
        summary = self.generate_summary()
        summary_path = self.base_dir / "summary.md"
        summary_path.write_text(summary)

        self.metadata["completed_at"] = datetime.now().isoformat()
        self.metadata["total_runs"] = sum(len(runs) for runs in self.results.values())
        self.metadata["total_passed"] = sum(
            sum(1 for r in runs if r.passed) for runs in self.results.values()
        )

        metadata_path = self.base_dir / "metadata.json"
        metadata_path.write_text(json.dumps(self.metadata, indent=2))

        print(f"\nExperiment results saved to: {self.base_dir}")
        print(f"Summary: {summary_path}")

        return summary_path


# =============================================================================
# PARALLEL SAVE HELPERS (for multiprocessing workers)
# =============================================================================

def save_events(base_dir: Path, treatment_name: str, rep: int, events: Dict[str, Any]):
    """Save events JSON."""
    events_dir = base_dir / "events"
    save_path = events_dir / f"{treatment_name.lower()}_rep{rep}.json"
    save_path.write_text(json.dumps(events, indent=2))
    return save_path


def save_raw(base_dir: Path, treatment_name: str, rep: int, stdout: str, stderr: str = None):
    """Save raw CLI output."""
    raw_dir = base_dir / "raw"
    stdout_path = raw_dir / f"{treatment_name.lower()}_rep{rep}_stdout.json"
    stdout_path.write_text(stdout)

    if stderr:
        stderr_path = raw_dir / f"{treatment_name.lower()}_rep{rep}_stderr.txt"
        stderr_path.write_text(stderr)


def save_report(base_dir: Path, treatment_name: str, rep: int, report: Dict[str, Any]):
    """Save treatment report."""
    reports_dir = base_dir / "reports"
    save_path = reports_dir / f"{treatment_name.lower()}_rep{rep}_report.json"
    save_path.write_text(json.dumps(report, indent=2))
    return save_path
