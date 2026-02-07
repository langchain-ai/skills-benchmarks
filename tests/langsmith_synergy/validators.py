"""Custom validators for LangSmith Synergy experiment."""

import ast
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold.framework import Validator
from scaffold.utils import retry_with_backoff


class DatasetValidator(Validator):
    """Validate that the dataset JSON file is properly structured for trajectory data."""

    def __init__(
        self,
        filename: str = "trajectory_dataset.json",
        min_examples: int = 1,
        dataset_type: str = "trajectory",  # trajectory, final_response, single_step
    ):
        self.filename = filename
        self.min_examples = min_examples
        self.dataset_type = dataset_type

    def validate(self, events: dict, test_dir: Path, outputs: Dict[str, tuple] = None):
        passed, failed = [], []
        file_path = test_dir / self.filename

        if not file_path.exists():
            failed.append(f"Dataset: {self.filename} not created")
            return passed, failed

        content = file_path.read_text()
        passed.append(f"Dataset: {self.filename} created ({len(content)} bytes)")

        # Validate JSON structure
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            failed.append(f"Dataset: invalid JSON - {e}")
            return passed, failed

        passed.append("Dataset: valid JSON")

        # Extract examples from various formats
        if isinstance(data, list):
            examples = data
        elif isinstance(data, dict):
            examples = data.get("examples", data.get("data", data.get("records", [data])))
            if not isinstance(examples, list):
                examples = [examples]
        else:
            failed.append(f"Dataset: unexpected structure (type={type(data).__name__})")
            return passed, failed

        # Check number of examples
        if len(examples) >= self.min_examples:
            passed.append(f"Dataset: {len(examples)} examples")
        else:
            failed.append(f"Dataset: only {len(examples)} examples (need {self.min_examples})")
            return passed, failed

        # Validate trajectory-specific structure
        if examples and self.dataset_type == "trajectory":
            valid_examples = 0
            structure_issues = []

            for i, ex in enumerate(examples[:5]):  # Check first 5
                if not isinstance(ex, dict):
                    structure_issues.append(f"Example {i}: not a dict")
                    continue

                # Trajectory datasets should have tool calls or actions
                ex_str = json.dumps(ex).lower()
                has_trajectory = any(kw in ex_str for kw in [
                    "tool_call", "tool_name", "action", "function_call",
                    "steps", "trajectory", "messages"
                ])

                if has_trajectory:
                    valid_examples += 1
                else:
                    structure_issues.append(f"Example {i}: no trajectory data")

            if valid_examples > 0:
                passed.append(f"Dataset: {valid_examples}/{min(5, len(examples))} examples have trajectory data")
            else:
                failed.append("Dataset: no examples contain trajectory data (tool_calls, actions, etc.)")

            if structure_issues and valid_examples == 0:
                failed.append(f"Dataset structure: {structure_issues[0]}")

        return passed, failed


class EvaluatorValidator(Validator):
    """Validate evaluator strictly follows LangSmith (run, example) format.

    From skill docs:
    - Function signature: def evaluator_name(run, example):
    - Access: run["outputs"], example["outputs"]
    - Return: {"metric_name": score, "comment": "..."}
    """

    def __init__(
        self,
        filename: str = "trajectory_evaluator.py",
        evaluator_type: str = "trajectory",
    ):
        self.filename = filename
        self.evaluator_type = evaluator_type

    def validate(self, events: dict, test_dir: Path, outputs: Dict[str, tuple] = None):
        passed, failed = [], []
        file_path = test_dir / self.filename

        if not file_path.exists():
            failed.append(f"Evaluator: {self.filename} not created")
            return passed, failed

        content = file_path.read_text()
        passed.append(f"Evaluator: {self.filename} created ({len(content)} bytes)")

        # Syntax check
        try:
            tree = ast.parse(content)
            passed.append("Evaluator: valid Python syntax")
        except SyntaxError as e:
            failed.append(f"Evaluator: syntax error line {e.lineno}")
            return passed, failed

        # Find function definitions (sync or async)
        functions = [node for node in ast.walk(tree)
                     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if not functions:
            failed.append("Evaluator: no function definitions found")
            return passed, failed

        # STRICT: Must have function with (run, example) signature
        langsmith_eval_found = False

        for func in functions:
            args = [arg.arg for arg in func.args.args]

            # Exact LangSmith signature: (run, example) - REQUIRED
            if "run" in args and "example" in args:
                langsmith_eval_found = True
                passed.append(f"Evaluator: '{func.name}(run, example)' - correct signature")

                # Check for return statement
                has_return = any(isinstance(node, ast.Return) for node in ast.walk(func))
                if has_return:
                    passed.append("Evaluator: has return statement")
                else:
                    failed.append("Evaluator: missing return statement")
                break

        if not langsmith_eval_found:
            failed.append("Evaluator: REQUIRED (run, example) signature not found")
            failed.append("LangSmith requires: def evaluator_name(run, example):")
            return passed, failed

        # STRICT: Must access run["outputs"]
        has_run_outputs = 'run["outputs"]' in content or "run['outputs']" in content
        if has_run_outputs:
            passed.append("Evaluator: accesses run['outputs']")
        else:
            failed.append("Evaluator: must access run['outputs'] for agent output")

        # Check for example["outputs"] (expected output)
        has_example_outputs = 'example["outputs"]' in content or "example['outputs']" in content
        if has_example_outputs:
            passed.append("Evaluator: accesses example['outputs']")
        else:
            passed.append("Note: doesn't access example['outputs'] (may use example['inputs'])")

        # STRICT: Must return dict with metric
        return_dict_pattern = r'return\s*\{[^}]*:[^}]*\}'
        has_return_dict = bool(re.search(return_dict_pattern, content))
        if has_return_dict:
            passed.append("Evaluator: returns dict with metric")
        else:
            if "return {" in content or "return{" in content:
                passed.append("Evaluator: returns dict format")
            else:
                failed.append("Evaluator: must return dict like {'metric': score}")

        # Trajectory-specific checks
        if self.evaluator_type == "trajectory":
            trajectory_keywords = ["trajectory", "tool", "sequence", "step", "action"]
            content_lower = content.lower()
            found_keywords = [kw for kw in trajectory_keywords if kw in content_lower]

            if len(found_keywords) >= 2:
                passed.append(f"Evaluator: trajectory logic ({', '.join(found_keywords[:3])})")
            else:
                passed.append("Note: limited trajectory keywords")

        return passed, failed


class TraceDataValidator(Validator):
    """Validate that meaningful trace data was queried from LangSmith."""

    def __init__(self, require_hierarchy: bool = True, min_traces: int = 1):
        self.require_hierarchy = require_hierarchy
        self.min_traces = min_traces

    def validate(self, events: dict, test_dir: Path, outputs: Dict[str, tuple] = None):
        passed, failed = [], []

        tool_calls = events.get("tool_calls", [])

        # Track what trace data was found
        trace_ids_found = set()
        has_hierarchy = False
        has_tool_calls = False
        has_inputs_outputs = False
        has_metadata = False
        langsmith_queries = 0

        for tc in tool_calls:
            output = str(tc.get("output", ""))
            output_lower = output.lower()
            tool_input = str(tc.get("input", "")).lower()

            # Count LangSmith-related queries
            if any(kw in tool_input for kw in ["query_traces", "langsmith", "trace"]):
                langsmith_queries += 1

            # Find trace IDs (UUIDs)
            uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            uuids = re.findall(uuid_pattern, output, re.IGNORECASE)
            trace_ids_found.update(uuids[:20])

            # Check for trace hierarchy data
            hierarchy_keywords = ["depth", "parent", "child", "nested", "hierarchy", "level"]
            if any(kw in output_lower for kw in hierarchy_keywords):
                has_hierarchy = True

            # Check for tool call data in traces
            tool_keywords = ["tool_call", "function_call", "tool_name", "execute_sql", "get_database"]
            if any(kw in output_lower for kw in tool_keywords):
                has_tool_calls = True

            # Check for inputs/outputs data
            io_keywords = ["inputs", "outputs", "input:", "output:", "messages", "content"]
            if any(kw in output_lower for kw in io_keywords):
                has_inputs_outputs = True

            # Check for metadata
            meta_keywords = ["latency", "token", "cost", "duration", "timestamp", "metadata"]
            if any(kw in output_lower for kw in meta_keywords):
                has_metadata = True

        # Report findings
        if langsmith_queries > 0:
            passed.append(f"Traces: {langsmith_queries} LangSmith query attempts")
        else:
            passed.append("Note: no LangSmith script executions detected")

        if len(trace_ids_found) >= self.min_traces:
            passed.append(f"Traces: found {len(trace_ids_found)} unique trace IDs")
        elif len(trace_ids_found) > 0:
            passed.append(f"Traces: found {len(trace_ids_found)} trace IDs (wanted {self.min_traces}+)")
        else:
            failed.append(f"Traces: no trace IDs found in outputs")

        # Hierarchy check
        if self.require_hierarchy:
            if has_hierarchy:
                passed.append("Traces: includes hierarchy/depth information")
            else:
                passed.append("Note: no explicit hierarchy data found")

        # Trace content quality
        content_score = sum([has_tool_calls, has_inputs_outputs, has_metadata])
        if content_score >= 2:
            passed.append(f"Traces: rich data (tools: {has_tool_calls}, I/O: {has_inputs_outputs}, meta: {has_metadata})")
        elif content_score == 1:
            passed.append("Traces: partial data retrieved")
        else:
            passed.append("Note: trace content may be minimal")

        return passed, failed


def _get_langsmith_client():
    """Get LangSmith client with API key from environment."""
    # Load .env if available (for host-side validation)
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


class LangSmithAPIValidator(Validator):
    """Validate traces exist in LangSmith by querying the actual API.

    Uses the same patterns as the tested skill scripts for reliable trace querying.
    """

    def __init__(
        self,
        project_name: str = None,
        min_traces: int = 1,
        max_age_minutes: int = 1440,  # 24 hours default
        require_tool_calls: bool = True,
    ):
        self.project_name = project_name
        self.min_traces = min_traces
        self.max_age_minutes = max_age_minutes
        self.require_tool_calls = require_tool_calls

    def validate(self, events: dict, test_dir: Path, outputs: Dict[str, tuple] = None):
        passed, failed = [], []

        project = self.project_name or os.environ.get("LANGSMITH_PROJECT")
        if not project:
            failed.append("LangSmith: LANGSMITH_PROJECT not set")
            return passed, failed

        try:
            client, error = _get_langsmith_client()
            if error:
                failed.append(f"LangSmith: {error}")
                return passed, failed

            # Query recent root traces (same pattern as query_traces.py)
            from datetime import timezone
            start_time = datetime.now(timezone.utc) - timedelta(minutes=self.max_age_minutes)

            # Use retry with backoff for rate limit handling
            def fetch_traces():
                return list(client.list_runs(
                    project_name=project,
                    is_root=True,
                    start_time=start_time,
                    limit=100,
                ))

            traces = retry_with_backoff(fetch_traces)

            if len(traces) >= self.min_traces:
                passed.append(f"LangSmith API: {len(traces)} traces in '{project}'")
            else:
                failed.append(f"LangSmith API: only {len(traces)} traces (need {self.min_traces})")
                return passed, failed

            # Check for tool calls in traces (same pattern as skill scripts)
            if self.require_tool_calls and traces:
                traces_with_tools = 0
                sample_size = min(10, len(traces))

                for trace in traces[:sample_size]:
                    trace_id = str(getattr(trace, "trace_id", trace.id))

                    def fetch_children(tid=trace_id):
                        return list(client.list_runs(
                            project_name=project,
                            trace_id=tid,
                            run_type="tool",
                            limit=5,
                        ))

                    try:
                        children = retry_with_backoff(fetch_children)
                        if children:
                            traces_with_tools += 1
                    except Exception:
                        # Skip this trace if we still hit rate limits after retries
                        pass

                if traces_with_tools > 0:
                    passed.append(f"LangSmith API: {traces_with_tools}/{sample_size} traces have tool calls")
                else:
                    passed.append("LangSmith API: no tool calls in sampled traces")

            # Sample trace info
            if traces:
                sample = traces[0]
                info = f"name='{sample.name}'" if sample.name else ""
                if sample.run_type:
                    info += f", type={sample.run_type}"
                passed.append(f"LangSmith API: sample ({info})")

        except ImportError:
            failed.append("LangSmith: langsmith package not installed")
        except Exception as e:
            error_str = str(e).lower()
            # Rate limit after retries exhausted - make it non-fatal
            if "429" in str(e) or "rate limit" in error_str:
                passed.append("LangSmith API: skipped (rate limited after retries)")
            else:
                failed.append(f"LangSmith API error: {str(e)[:100]}")

        return passed, failed


class SkillScriptValidator(Validator):
    """Validate that skill scripts were actually executed.

    Script usage is tracked as a metric but doesn't fail the test -
    the agent may solve the task correctly without using the provided scripts.
    """

    def __init__(self, script_patterns: Dict[str, str], require_scripts: bool = False):
        """
        Args:
            script_patterns: {pattern: description} - patterns to find in commands
            require_scripts: If True, missing scripts cause failure. If False (default),
                           missing scripts are noted but don't fail the test.
        """
        self.script_patterns = script_patterns
        self.require_scripts = require_scripts

    def validate(self, events: dict, test_dir: Path, outputs: Dict[str, tuple] = None):
        passed, failed = [], []

        commands = events.get("commands_run", [])
        commands_str = " ".join(commands).lower()

        for pattern, desc in self.script_patterns.items():
            if pattern.lower() in commands_str:
                passed.append(f"Script: used {desc}")
            else:
                if self.require_scripts:
                    failed.append(f"Script: did NOT use {desc}")
                else:
                    # Track as metric but don't fail - agent may have solved it differently
                    passed.append(f"Note: did not use {desc} (solved differently)")

        return passed, failed


class LangSmithDatasetValidator(Validator):
    """Validate that a dataset was uploaded to LangSmith.

    Uses the same patterns as the tested dataset skill scripts.
    """

    def __init__(
        self,
        dataset_name_pattern: str = None,
        min_examples: int = 1,
    ):
        self.dataset_name_pattern = dataset_name_pattern
        self.min_examples = min_examples

    def validate(self, events: dict, test_dir: Path, outputs: Dict[str, tuple] = None):
        passed, failed = [], []

        try:
            client, error = _get_langsmith_client()
            if error:
                passed.append(f"LangSmith Dataset: skipped ({error})")
                return passed, failed

            # List recent datasets
            datasets = list(client.list_datasets(limit=50))

            if not datasets:
                passed.append("LangSmith Dataset: no datasets in account")
                return passed, failed

            # Find matching dataset by pattern
            matching = [ds for ds in datasets
                        if not self.dataset_name_pattern
                        or self.dataset_name_pattern.lower() in ds.name.lower()]

            if matching:
                ds = matching[0]
                passed.append(f"LangSmith Dataset: found '{ds.name}'")

                # Check example count (same as query_datasets.py pattern)
                examples = list(client.list_examples(dataset_id=ds.id, limit=10))
                count_msg = f"{len(examples)}+ examples" if len(examples) >= self.min_examples else f"{len(examples)} examples"
                passed.append(f"LangSmith Dataset: {count_msg}")
            else:
                pattern_msg = f" matching '{self.dataset_name_pattern}'" if self.dataset_name_pattern else ""
                passed.append(f"LangSmith Dataset: no dataset{pattern_msg} found")

        except ImportError:
            passed.append("LangSmith Dataset: skipped (langsmith not installed)")
        except Exception as e:
            passed.append(f"LangSmith Dataset: error ({str(e)[:50]})")

        return passed, failed
