"""Test runner for validation scripts.

Handles all boilerplate so contributors just write check functions.
Each check function receives a TestRunner and must call runner.passed()
or runner.failed() — returning without calling either is an error.

Example:

    from scaffold.python.validation.runner import TestRunner

    def check_has_function(runner):
        source = runner.read("agent.py")
        if "def my_function" in source:
            runner.passed("has my_function")
        else:
            runner.failed("missing my_function")

    def check_runs(runner):
        output = runner.execute("agent.py")
        if output is not None:
            runner.passed("produced output")
        else:
            runner.failed("execution failed")

    if __name__ == "__main__":
        TestRunner.run([check_has_function, check_runs])
"""

import importlib.util
import json
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType

from scaffold.python.validation.core import (
    TEST_CONTEXT_FILE,
    load_test_context,
    write_test_results,
)


class TestRunner:
    """Runner that handles boilerplate for validation test scripts.

    Properties:
        runner.artifacts  — target artifact paths (from task.toml via _test_context.json)
        runner.context    — full run context dict (run_id, events, langsmith_env, etc.)

    Methods:
        runner.passed(msg)           — record a passing check
        runner.failed(msg)           — record a failing check
        runner.read(path)            — read a file's contents (returns "" if not found)
        runner.execute(path, ...)    — run a file in a subprocess, return stdout
    """

    def __init__(self):
        self.context = load_test_context()
        self.artifacts: list[str] = self.context.get("target_artifacts", [])
        self._passed: list[str] = []
        self._failed: list[str] = []
        self._error: str | None = None
        self._check_called = False
        self._module_cache: dict[str, ModuleType | None] = {}  # instance-level cache

    def passed(self, message: str) -> None:
        """Record a passing check."""
        self._check_called = True
        self._passed.append(message)

    def failed(self, message: str) -> None:
        """Record a failing check."""
        self._check_called = True
        self._failed.append(message)

    def read(self, path: str) -> str:
        """Read a file's contents. Returns empty string if not found."""
        p = Path(path)
        if p.is_file():
            try:
                return p.read_text()
            except Exception:
                return ""
        return ""

    def load_module(self, path: str) -> ModuleType | None:
        """Import a Python file as a module. Returns the module or None.

        Cached per path — calling with the same path returns the same module
        (avoids re-executing side effects). On first failure, records a failed
        check and caches None. Subsequent calls return None and record a
        cached failure (so the calling check satisfies the passed/failed requirement).
        """
        target = Path(path).resolve()
        cache_key = str(target)
        if cache_key in self._module_cache:
            cached = self._module_cache[cache_key]
            if cached is None:
                # Already failed — record silently so each check shows the failure
                self.failed(f"import failed: {path} (cached)")
            return cached
        if not target.is_file():
            self.failed(f"cannot load {path}: file not found")
            self._module_cache[cache_key] = None
            return None
        try:
            module_name = f"_bench_{target.stem}_{id(target)}"
            spec = importlib.util.spec_from_file_location(module_name, str(target))
            if spec is None or spec.loader is None:
                self.failed(f"cannot load {path}: invalid module spec")
                self._module_cache[cache_key] = None
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._module_cache[cache_key] = module
            return module
        except Exception as e:
            self.failed(f"import error ({path}): {e}")
            return None

    def execute(self, path: str, args: list[str] | None = None, timeout: int = 30) -> str | None:
        """Run a file in a subprocess (inside the Docker container).

        Returns stdout on success, stdout+stderr on non-zero exit,
        or None on failure (also records a failed check).
        """
        target = Path(path)
        if not target.exists():
            self.failed(f"cannot execute {path}: file not found")
            return None
        cmd = [sys.executable, str(target)] + (args or [])
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if result.returncode != 0:
                return result.stdout + result.stderr
            return result.stdout
        except subprocess.TimeoutExpired:
            self.failed(f"execution timed out ({timeout}s)")
            return None
        except Exception as e:
            self.failed(f"execution error: {e}")
            return None

    def _results(self) -> dict:
        return {
            "passed": self._passed,
            "failed": self._failed,
            "error": self._error,
        }

    def _run_check_traced(self, check_fn, check_name: str):
        """Run a check function, wrapping in a trace if langsmith is available."""
        passed_before = len(self._passed)
        failed_before = len(self._failed)

        def _run():
            check_fn(self)
            if not self._check_called:
                self._failed.append(f"{check_name}: check did not call passed() or failed()")

        try:
            from langsmith.run_helpers import trace as ls_trace

            with ls_trace(name=check_name, run_type="chain") as run:
                _run()
                if run:
                    run.outputs = {
                        "passed": self._passed[passed_before:],
                        "failed": self._failed[failed_before:],
                    }
        except ImportError:
            _run()

    @staticmethod
    @contextmanager
    def _eval_trace_context():
        """Create a LangSmith trace context if eval trace env vars are set.

        Uses distributed tracing headers to nest LLM calls
        (e.g. evaluate_with_schema) under the host-side eval span.
        """
        trace_header = os.environ.get("BENCH_EVAL_LANGSMITH_TRACE")
        baggage = os.environ.get("BENCH_EVAL_BAGGAGE")

        if not trace_header:
            yield
            return

        try:
            import langsmith

            headers: dict[str, str] = {"langsmith-trace": trace_header}
            if baggage:
                headers["baggage"] = baggage
            with langsmith.tracing_context(parent=headers):
                yield
        except Exception:
            # Tracing failed — run checks without tracing
            yield

    @staticmethod
    def run(checks: list) -> None:
        """Run check functions and handle all output.

        Each check function receives a TestRunner instance and MUST call
        runner.passed() or runner.failed() at least once. Not calling
        either is treated as an error.

        Args:
            checks: List of check functions. Function name is used as
                    the check name (underscores replaced with spaces).
        """
        runner = TestRunner()

        if not runner.context:
            print(f"Error: {TEST_CONTEXT_FILE} not found or empty", file=sys.stderr)
            sys.exit(1)

        with TestRunner._eval_trace_context():
            for check_fn in checks:
                check_name = check_fn.__name__.replace("check_", "").replace("_", " ")
                runner._check_called = False
                try:
                    runner._run_check_traced(check_fn, check_name)
                except Exception as e:
                    runner._failed.append(f"{check_name}: {e}")

        results = runner._results()
        print(json.dumps(results, indent=2))
        write_test_results(results)
        sys.exit(1 if results["failed"] else 0)
