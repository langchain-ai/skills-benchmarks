"""Output parsing, event extraction, and experiment logging for Claude CLI."""

import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable

PROJECT_ROOT = Path(__file__).parent.parent.parent  # scaffold/python/ -> scaffold/ -> project root
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
    run_id: str = ""  # Unique ID for finding LangSmith assets (test-{run_id})

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
    description: str = ""  # Human-readable description of what this column checks

    def get_value(self, result: TreatmentResult) -> str:
        return self.extract(result)

    def get_aggregate(self, runs: List[TreatmentResult]) -> str:
        if self.aggregate:
            return self.aggregate(runs)
        return self.extract(runs[0]) if runs else "N/A"


def bool_column(name: str, pattern: str, description: str = None) -> ReportColumn:
    """Column that checks if pattern exists in passed checks."""
    return ReportColumn(
        name=name,
        extract=lambda r: "Yes" if r.has_check(pattern) else "No",
        aggregate=lambda runs: f"{sum(1 for r in runs if r.has_check(pattern))}/{len(runs)}",
        description=description or f"Checks if any passed check contains: `{pattern}`",
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

    return ReportColumn(
        name=name,
        extract=extract,
        aggregate=aggregate,
        description="Checks for [GOOD] or [LOW] quality rating from LLM evaluation",
    )


def default_columns() -> List[ReportColumn]:
    """Standard columns: Checks, Turns, Duration, Tools."""
    return [
        ReportColumn(
            name="Checks",
            extract=lambda r: _checks_single(r),
            aggregate=lambda runs: _checks_aggregate(runs),
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


def _checks_single(r) -> str:
    """Format checks for a single run."""
    passed = len(r.checks_passed)
    total = passed + len(r.checks_failed)
    pct = (passed / total * 100) if total > 0 else 0
    return f"{passed}/{total} ({pct:.0f}%)"


def _checks_aggregate(runs: List) -> str:
    """Aggregate checks passed across runs."""
    total_passed = sum(len(r.checks_passed) for r in runs)
    total_checks = sum(len(r.checks_passed) + len(r.checks_failed) for r in runs)
    pct = (total_passed / total_checks * 100) if total_checks > 0 else 0
    return f"{total_passed}/{total_checks} ({pct:.0f}%)"


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

    def __init__(
        self,
        experiment_name: str = None,
        columns: List[ReportColumn] = None,
        experiment_id: str = None,
    ):
        """Create experiment logger.

        Args:
            experiment_name: Name for this experiment (used to generate ID if not provided)
            columns: Custom columns for reporting (in addition to defaults)
            experiment_id: Existing experiment ID to join (for parallel workers)
        """
        if experiment_id:
            # Join existing experiment
            self.experiment_id = experiment_id
            self.name = experiment_id.rsplit("_", 2)[0] if "_" in experiment_id else experiment_id
            self.timestamp = experiment_id.rsplit("_", 1)[-1] if "_" in experiment_id else ""
        else:
            # Create new experiment
            self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.name = experiment_name or f"experiment_{self.timestamp}"
            self.experiment_id = f"{self.name}_{self.timestamp}"

        self.base_dir = LOGS_DIR / "experiments" / self.experiment_id

        # Create subdirectories
        self.events_dir = self.base_dir / "events"
        self.reports_dir = self.base_dir / "reports"
        self.raw_dir = self.base_dir / "raw"

        for d in [self.events_dir, self.reports_dir, self.raw_dir]:
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

        # Column definitions section
        custom_cols = [c for c in self.columns if c.description]
        if custom_cols:
            lines.append("## Column Definitions\n")
            for col in custom_cols:
                lines.append(f"- **{col.name}**: {col.description}")
            lines.append("")

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
        total_checks_passed = sum(sum(len(r.checks_passed) for r in runs) for runs in self.results.values())
        total_checks = sum(sum(len(r.checks_passed) + len(r.checks_failed) for r in runs) for runs in self.results.values())
        check_pct = (total_checks_passed / total_checks * 100) if total_checks > 0 else 0

        lines.append("## Summary\n")
        lines.append(f"- **Total Runs:** {total_runs}")
        lines.append(f"- **Checks Passed:** {total_checks_passed}/{total_checks} ({check_pct:.1f}%)")
        lines.append("")

        # Detailed per-treatment breakdown
        lines.append("## Treatment Details\n")
        for name, runs in self.results.items():
            treatment_passed = sum(len(r.checks_passed) for r in runs)
            treatment_total = sum(len(r.checks_passed) + len(r.checks_failed) for r in runs)
            treatment_pct = (treatment_passed / treatment_total * 100) if treatment_total > 0 else 0
            lines.append(f"### {name} ({treatment_passed}/{treatment_total} checks, {treatment_pct:.0f}%)\n")

            for i, r in enumerate(runs, 1):
                run_label = f"Run {i}" if has_reps else "Result"
                run_passed = len(r.checks_passed)
                run_total = run_passed + len(r.checks_failed)
                run_pct = (run_passed / run_total * 100) if run_total > 0 else 0
                run_id_str = f" (run_id: {r.run_id})" if r.run_id else ""
                lines.append(f"**{run_label}:** {run_passed}/{run_total} checks ({run_pct:.0f}%){run_id_str}")

                # Show metrics
                metrics = []
                if r.turns:
                    metrics.append(f"Turns: {r.turns}")
                if r.duration:
                    metrics.append(f"Duration: {r.duration:.0f}s")
                if r.tool_calls:
                    metrics.append(f"Tool calls: {r.tool_calls}")
                if metrics:
                    lines.append(f"- Metrics: {', '.join(metrics)}")

                # Show all passed checks
                if r.checks_passed:
                    lines.append(f"- Passed checks ({len(r.checks_passed)}):")
                    for check in r.checks_passed:
                        lines.append(f"  - {check}")

                # Show all failed checks
                if r.checks_failed:
                    lines.append(f"- Failed checks ({len(r.checks_failed)}):")
                    for check in r.checks_failed:
                        lines.append(f"  - {check}")

                lines.append("")

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
    events_dir.mkdir(parents=True, exist_ok=True)
    save_path = events_dir / f"{treatment_name.lower()}_rep{rep}.json"
    save_path.write_text(json.dumps(events, indent=2))
    return save_path


def save_raw(base_dir: Path, treatment_name: str, rep: int, stdout: str, stderr: str = None):
    """Save raw CLI output."""
    raw_dir = base_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = raw_dir / f"{treatment_name.lower()}_rep{rep}_stdout.json"
    stdout_path.write_text(stdout)

    if stderr:
        stderr_path = raw_dir / f"{treatment_name.lower()}_rep{rep}_stderr.txt"
        stderr_path.write_text(stderr)


def save_report(base_dir: Path, treatment_name: str, rep: int, report: Dict[str, Any]):
    """Save treatment report."""
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    save_path = reports_dir / f"{treatment_name.lower()}_rep{rep}_report.json"
    save_path.write_text(json.dumps(report, indent=2))
    return save_path
