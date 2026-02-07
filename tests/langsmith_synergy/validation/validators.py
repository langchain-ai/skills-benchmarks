"""Validators for LangSmith Synergy experiment."""

import ast
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scaffold.validation import Validator
from scaffold.utils import (
    retry_with_backoff,
    read_json_file,
    get_field,
    get_nested_field,
    normalize_score,
    extract_score,
    run_python_in_docker,
)


# =============================================================================
# LANGSMITH HELPERS
# =============================================================================

def get_langsmith_client():
    """Get LangSmith client. Returns (client, error_string)."""
    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)
    except ImportError:
        pass

    from langsmith import Client
    api_key = os.environ.get("LANGSMITH_API_KEY")
    if not api_key:
        return None, "LANGSMITH_API_KEY not set"
    return Client(api_key=api_key), None


def extract_examples(data) -> list:
    """Extract examples list from various dataset formats."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("examples") or data.get("data") or [data]
    return []


def is_rate_limited(error: Exception) -> bool:
    """Check if error is a rate limit error."""
    msg = str(error).lower()
    return "429" in msg or "rate limit" in msg


# =============================================================================
# VALIDATORS
# =============================================================================

class TraceDataValidator(Validator):
    """Validate traces exist and match expected ground truth."""

    def __init__(self, min_traces: int = 1, max_age_minutes: int = 1440):
        self.min_traces = min_traces
        self.max_age_minutes = max_age_minutes

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None) -> Tuple[List[str], List[str]]:
        passed, failed = [], []

        project = os.environ.get("LANGSMITH_PROJECT")
        if not project:
            return passed, ["Traces: LANGSMITH_PROJECT not set"]

        client, error = get_langsmith_client()
        if error:
            return passed, [f"Traces: {error}"]

        try:
            # Query recent traces
            start_time = datetime.now(timezone.utc) - timedelta(minutes=self.max_age_minutes)
            traces = retry_with_backoff(lambda: list(client.list_runs(
                project_name=project, is_root=True, start_time=start_time, limit=20
            )))

            if len(traces) < self.min_traces:
                return passed, [f"Traces: only {len(traces)} in project (need {self.min_traces})"]

            passed.append(f"Traces: {len(traces)} available in '{project}'")

            # Count traces with tool calls
            traces_with_tools = sum(1 for trace in traces[:5] if self._has_tool_calls(client, project, trace))
            if traces_with_tools > 0:
                passed.append(f"Traces: {traces_with_tools}/5 have tool calls")

            # Compare against ground truth
            gt_data, _ = read_json_file(test_dir / "expected_traces.json")
            if gt_data:
                passed.append(f"Ground truth: {len(gt_data)} traces")
                match_passed, match_failed = self._compare_to_ground_truth(client, project, gt_data)
                passed.extend(match_passed)
                failed.extend(match_failed)

        except ImportError:
            failed.append("Traces: langsmith not installed")
        except Exception as e:
            if is_rate_limited(e):
                passed.append("Traces: skipped (rate limited)")
            else:
                failed.append(f"Traces: {str(e)[:60]}")

        return passed, failed

    def _has_tool_calls(self, client, project: str, trace) -> bool:
        """Check if trace has tool calls."""
        try:
            tid = str(getattr(trace, "trace_id", trace.id))
            tools = retry_with_backoff(lambda: list(client.list_runs(
                project_name=project, trace_id=tid, run_type="tool", limit=5
            )))
            return bool(tools)
        except Exception:
            return False

    def _compare_to_ground_truth(self, client, project: str, expected: list) -> Tuple[List[str], List[str]]:
        """Compare fetched traces against expected ground truth."""
        passed, failed = [], []

        if not expected:
            return passed, failed

        matches = 0
        for exp in expected[:5]:  # Check first 5
            exp_id = exp.get("trace_id")
            exp_tools = exp.get("tool_sequence", [])

            if not exp_id:
                continue

            # Get actual tool sequence for this trace
            try:
                actual_tools = self._get_tool_sequence(client, project, exp_id)
                if actual_tools == exp_tools:
                    matches += 1
                elif set(actual_tools) == set(exp_tools):
                    matches += 0.5  # Partial match (same tools, different order)
            except Exception:
                pass

        total = min(5, len(expected))
        if matches >= total * 0.8:
            passed.append(f"Traces: {int(matches)}/{total} match ground truth")
        elif matches > 0:
            passed.append(f"Traces: {int(matches)}/{total} partial match")
        else:
            failed.append(f"Traces: 0/{total} match ground truth")

        return passed, failed

    def _get_tool_sequence(self, client, project: str, trace_id: str) -> list:
        """Get ordered tool sequence for a trace."""
        tools = retry_with_backoff(lambda: list(client.list_runs(
            project_name=project, trace_id=trace_id, run_type="tool", limit=50
        )))
        # Sort by start time and return names
        tools.sort(key=lambda t: t.start_time or datetime.min)
        return [t.name for t in tools]


class DatasetValidator(Validator):
    """Validate dataset file structure, ground truth match, and LangSmith upload."""

    def __init__(
        self,
        filename: str = "trajectory_dataset.json",
        min_examples: int = 1,
        dataset_type: str = "trajectory",
        verify_upload: bool = True,
        upload_prefix: str = "test-",
    ):
        self.filename = filename
        self.min_examples = min_examples
        self.dataset_type = dataset_type
        self.verify_upload = verify_upload
        self.upload_prefix = upload_prefix

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None) -> Tuple[List[str], List[str]]:
        passed, failed = [], []

        # Read dataset file
        data, error = read_json_file(test_dir / self.filename)
        if error:
            return passed, [f"Dataset: {error}"]

        passed.append(f"Dataset: {self.filename} created")
        examples = extract_examples(data)

        if len(examples) < self.min_examples:
            return passed, [f"Dataset: {len(examples)} examples (need {self.min_examples})"]

        passed.append(f"Dataset: {len(examples)} examples")

        # Check structure
        sample = examples[:10]
        valid_io = sum(1 for ex in sample if self._has_io(ex))
        has_traj = sum(1 for ex in sample if self._get_trajectory(ex))

        if valid_io > 0:
            passed.append(f"Dataset: {valid_io}/{len(sample)} have input/output")
        else:
            failed.append("Dataset: no input/output structure")

        if self.dataset_type == "trajectory":
            if has_traj > 0:
                passed.append(f"Dataset: {has_traj}/{len(sample)} have trajectory")
            else:
                failed.append("Dataset: no trajectory data")

        # Compare to ground truth
        gt_data, _ = read_json_file(test_dir / "expected_dataset.json")
        if gt_data:
            gtp, gtf = self._compare_ground_truth(examples, gt_data)
            passed.extend(gtp)
            failed.extend(gtf)

        # Verify LangSmith upload
        if self.verify_upload:
            up, uf = self._verify_upload()
            passed.extend(up)
            failed.extend(uf)

        return passed, failed

    def _has_io(self, ex: dict) -> bool:
        if not isinstance(ex, dict):
            return False
        return ("inputs" in ex or "input" in ex) and ("outputs" in ex or "output" in ex)

    def _get_trajectory(self, ex: dict) -> list:
        """Extract trajectory from example (various formats)."""
        if not isinstance(ex, dict):
            return []
        traj = get_field(ex, "trajectory", "expected_trajectory")
        if not traj:
            traj = get_nested_field(ex, ["outputs", "output"], ["expected_trajectory", "trajectory"])
        return traj if isinstance(traj, list) else []

    def _compare_ground_truth(self, actual: list, expected: dict) -> Tuple[List[str], List[str]]:
        """Compare generated dataset against expected ground truth.

        Matching criteria:
        - Match by trace_id
        - Check both trajectory (exact) and inputs (exact)
        - Full match = 1 point, partial (trajectory or overlap) = 0.5 points
        - 80% threshold to pass
        """
        passed, failed = [], []
        exp_examples = extract_examples(expected)

        if not exp_examples:
            return passed, failed

        # Build lookup by trace_id
        exp_lookup = {
            ex.get("trace_id"): {
                "trajectory": self._get_trajectory(ex),
                "inputs": ex.get("inputs", {})
            }
            for ex in exp_examples
        }
        matches = 0

        for ex in actual[:10]:
            tid = ex.get("trace_id")
            if tid not in exp_lookup:
                continue

            actual_traj = self._get_trajectory(ex)
            actual_inputs = ex.get("inputs", {})
            expected_traj = exp_lookup[tid]["trajectory"]
            expected_inputs = exp_lookup[tid]["inputs"]

            traj_match = actual_traj and expected_traj and actual_traj == expected_traj
            inputs_match = actual_inputs == expected_inputs

            if traj_match and inputs_match:
                matches += 1
            elif traj_match:
                matches += 0.5
            else:
                # Check for partial overlap (any common tools)
                try:
                    if set(actual_traj or []) & set(expected_traj or []):
                        matches += 0.5
                except TypeError:
                    pass  # Unhashable types (dicts) = wrong format, no credit

        total = min(len(actual), len(exp_examples), 10)
        if total > 0:
            ratio = matches / total
            if ratio >= 0.8:
                passed.append(f"Dataset: {matches}/{total} match ground truth")
            else:
                failed.append(f"Dataset: {matches}/{total} match ground truth (need 80%)")

        return passed, failed

    def _verify_upload(self) -> Tuple[List[str], List[str]]:
        """Verify dataset was uploaded to LangSmith."""
        passed, failed = [], []

        client, error = get_langsmith_client()
        if error:
            return [f"Upload: skipped ({error})"], []

        try:
            datasets = list(client.list_datasets())
            matching = [d for d in datasets if d.name.startswith(self.upload_prefix)]

            if not matching:
                return [], [f"Upload: no dataset with prefix '{self.upload_prefix}' in LangSmith"]

            recent = max(matching, key=lambda d: getattr(d, 'created_at', d.name))
            passed.append(f"Upload: found '{recent.name}' in LangSmith")

            count = getattr(recent, 'example_count', None)
            if count is not None:
                passed.append(f"Upload: {count} examples in LangSmith")

        except Exception as e:
            if is_rate_limited(e):
                passed.append("Upload: skipped (rate limited)")
            else:
                failed.append(f"Upload: {str(e)[:40]}")

        return passed, failed


class EvaluatorValidator(Validator):
    """Validate evaluator Python file and run test cases in Docker (safe execution)."""

    def __init__(
        self,
        filename: str = "trajectory_evaluator.py",
        test_cases_filename: str = "evaluator_test_cases.json",
        verify_upload: bool = False,
        upload_prefix: str = "test-",
        max_age_minutes: int = 30,
    ):
        self.filename = filename
        self.test_cases_filename = test_cases_filename
        self.verify_upload = verify_upload
        self.upload_prefix = upload_prefix
        self.max_age_minutes = max_age_minutes

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None) -> Tuple[List[str], List[str]]:
        passed, failed = [], []

        path = test_dir / self.filename
        if not path.exists():
            return passed, [f"Evaluator: {self.filename} not created"]

        content = path.read_text()
        passed.append(f"Evaluator: {self.filename} created ({len(content)} bytes)")

        # Parse and find evaluator function (safe - just AST parsing, no exec)
        func_name, error = self._find_evaluator_function(content)
        if error:
            return passed, [error]

        passed.append("Evaluator: valid syntax")
        passed.append(f"Evaluator: {func_name}(run, example)")

        # Run test cases in Docker (safe execution)
        test_passed, test_failed = self._run_test_cases_in_docker(test_dir, func_name)
        passed.extend(test_passed)
        failed.extend(test_failed)

        # Verify upload to LangSmith
        if self.verify_upload:
            up, uf = self._verify_upload()
            passed.extend(up)
            failed.extend(uf)

        return passed, failed

    def _find_evaluator_function(self, content: str) -> Tuple[str, str]:
        """Parse code and find evaluator function name (safe - no execution)."""
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return None, f"Evaluator: syntax error line {e.lineno}"

        # Find function with (run, example) args
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in node.args.args]
                if "run" in args and "example" in args:
                    return node.name, None

        return None, "Evaluator: no (run, example) function"

    def _run_test_cases_in_docker(self, test_dir: Path, func_name: str) -> Tuple[List[str], List[str]]:
        """Run evaluator test cases in Docker for safe execution."""
        passed, failed = [], []

        # Check for test cases
        test_cases_path = test_dir / self.test_cases_filename
        if not test_cases_path.exists():
            passed.append("Evaluator: no test cases (skipping execution test)")
            return passed, failed

        # Copy runner script to test directory
        runner_src = Path(__file__).parent / "eval_runner.py"
        runner_dst = test_dir / "_eval_runner.py"
        runner_dst.write_text(runner_src.read_text())

        try:
            # Run: python _eval_runner.py <module> <func> <test_cases.json>
            module_name = self.filename.replace(".py", "")
            args = [module_name, func_name, self.test_cases_filename]
            success, output = run_python_in_docker(test_dir, "_eval_runner.py", timeout=60, args=args)

            # Parse results from output
            for line in output.split("\n"):
                if line.startswith("EVALUATOR_RESULTS:"):
                    results = json.loads(line.replace("EVALUATOR_RESULTS:", ""))
                    tests_passed = sum(1 for r in results if r.get("passed"))
                    total = len(results)

                    if tests_passed == total:
                        passed.append(f"Evaluator: {tests_passed}/{total} tests passed")
                    elif tests_passed > total // 2:
                        passed.append(f"Evaluator: {tests_passed}/{total} tests (partial)")
                    else:
                        failed.append(f"Evaluator: {tests_passed}/{total} tests passed")
                    return passed, failed

            # No results found in output
            if success:
                passed.append("Evaluator: executed (no test results)")
            else:
                failed.append("Evaluator: execution failed")

        except Exception as e:
            failed.append(f"Evaluator: docker error - {str(e)[:40]}")
        finally:
            runner_dst.unlink(missing_ok=True)

        return passed, failed

    def _verify_upload(self) -> Tuple[List[str], List[str]]:
        """Verify evaluator was uploaded to LangSmith recently."""
        passed, failed = [], []

        client, error = get_langsmith_client()
        if error:
            return [f"Evaluator upload: skipped ({error})"], []

        try:
            # List evaluators and check for matching prefix
            evaluators = list(client.list_evaluators())
            matching = [e for e in evaluators if e.name.startswith(self.upload_prefix)]

            if not matching:
                return [], [f"Evaluator upload: no evaluator with prefix '{self.upload_prefix}' in LangSmith"]

            # Filter by age - only consider recently created evaluators
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.max_age_minutes)
            recent_matching = [
                e for e in matching
                if hasattr(e, 'created_at') and e.created_at and e.created_at >= cutoff
            ]

            if not recent_matching:
                # Fall back to any matching if we can't filter by time
                recent = max(matching, key=lambda e: getattr(e, 'created_at', None) or e.name)
                passed.append(f"Evaluator upload: found '{recent.name}' (age unknown)")
            else:
                recent = max(recent_matching, key=lambda e: e.created_at)
                passed.append(f"Evaluator upload: found '{recent.name}' in LangSmith")

        except AttributeError:
            # Older LangSmith SDK may not have list_evaluators
            passed.append("Evaluator upload: skipped (SDK version)")
        except Exception as e:
            if is_rate_limited(e):
                passed.append("Evaluator upload: skipped (rate limited)")
            else:
                failed.append(f"Evaluator upload: {str(e)[:40]}")

        return passed, failed


class SkillScriptValidator(Validator):
    """Validate that skill scripts were used in commands."""

    def __init__(self, script_patterns: Dict[str, str], require_scripts: bool = False):
        self.script_patterns = script_patterns
        self.require_scripts = require_scripts

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None) -> Tuple[List[str], List[str]]:
        passed, failed = [], []
        commands = " ".join(events.get("commands_run", [])).lower()

        for pattern, desc in self.script_patterns.items():
            if pattern.lower() in commands:
                passed.append(f"Script: {desc}")
            elif self.require_scripts:
                failed.append(f"Script: missing {desc}")
            else:
                passed.append(f"Note: no {desc}")

        return passed, failed
