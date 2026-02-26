"""Execution-based tests for deep agents memory/subagent fixes.

These tests verify actual behavior by inspecting the agent configuration
and testing the routing logic.

The broken code has bugs from multiple skill areas:

From da_memory:
1. CompositeBackend longest-prefix routing - /memory/cache/ matches more specific route
   than /memory/, so files saved there use StateBackend (ephemeral) not StoreBackend
2. Path choice for persistence - should use /memory/ directly, not /memory/cache/

From da_subagents:
3. Skill inheritance asymmetry - custom subagents DON'T inherit main agent's skills
   (only general-purpose subagent does)
4. Subagent interrupts require checkpointer - interrupt_on without checkpointer won't work
"""

import ast
import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TestContext:
    """Shared context for test execution."""

    module_path: str
    source: str = ""
    module: Any | None = None
    results: dict = field(default_factory=lambda: {"passed": [], "failed": [], "error": None})

    def load(self) -> bool:
        """Load source and module. Returns True if successful."""
        # Add module directory to path
        module_dir = os.path.dirname(os.path.abspath(self.module_path))
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)

        # Read source
        try:
            with open(self.module_path) as f:
                self.source = f.read()
        except Exception as e:
            self.results["error"] = f"Failed to read file: {e}"
            return False

        # Parse AST to validate syntax
        try:
            ast.parse(self.source)
        except SyntaxError as e:
            self.results["error"] = f"Syntax error in file: {e}"
            return False

        # Try to import module
        try:
            spec = importlib.util.spec_from_file_location("agent_system", self.module_path)
            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)
        except Exception:
            self.module = None

        return True

    def pass_test(self, name: str):
        """Mark a test as passed."""
        self.results["passed"].append(name)

    def fail_test(self, name: str, reason: str):
        """Mark a test as failed with reason."""
        self.results["failed"].append(f"{name}: {reason}")


# =============================================================================
# Test 1: Route Hierarchy
# =============================================================================


def test_route_hierarchy(ctx: TestContext):
    """Check that /memory/cache/ doesn't override /memory/ with ephemeral storage.

    Bug: CompositeBackend uses longest-prefix matching, so /memory/cache/
    matches before /memory/, making cache storage ephemeral when it shouldn't be.
    """
    TEST_NAME = "route_hierarchy_correct"

    # Try execution-based check first
    if ctx.module and hasattr(ctx.module, "create_agent_system"):
        try:
            agent = ctx.module.create_agent_system()
            backend = getattr(agent, "backend", None) or getattr(agent, "_backend", None)

            if backend and hasattr(backend, "sorted_routes"):
                for prefix, backend_instance in backend.sorted_routes:
                    backend_type = type(backend_instance).__name__
                    if "/memory/cache/" in prefix and "State" in backend_type:
                        ctx.fail_test(
                            TEST_NAME,
                            "longer prefix routes take precedence - "
                            "/memory/cache/ overrides /memory/, making cache ephemeral",
                        )
                        return
                ctx.pass_test(TEST_NAME)
                return
        except Exception:
            pass  # Fall back to source check

    # Source-based fallback
    _check_route_hierarchy_source(ctx)


def _check_route_hierarchy_source(ctx: TestContext):
    """Source-based route hierarchy check."""
    TEST_NAME = "route_hierarchy_correct"
    composite_routes = re.search(r"routes\s*=\s*\{([^}]+)\}", ctx.source, re.DOTALL)

    if not composite_routes:
        ctx.pass_test(TEST_NAME)
        return

    routes_content = composite_routes.group(1)

    # Check if /memory/cache/ uses StateBackend (ephemeral)
    cache_is_ephemeral = (
        "StateBackend" in routes_content
        and "/memory/cache/" in routes_content
        and re.search(r"/memory/cache/.*StateBackend", routes_content, re.DOTALL)
    )

    if not cache_is_ephemeral:
        # Either no cache route, or cache uses StoreBackend - OK
        ctx.pass_test(TEST_NAME)
        return

    # Cache is ephemeral - only a problem if prefs are saved there
    # Look for actual path usage, not comments (match quotes or content strings)
    prefs_use_cache = re.search(r'["\'].*?/memory/cache/prefs', ctx.source)

    if prefs_use_cache:
        ctx.fail_test(
            TEST_NAME,
            "longer prefix routes take precedence - "
            "/memory/cache/ overrides /memory/, making cache ephemeral",
        )
    else:
        # Prefs don't use cache path, so ephemeral cache is fine
        ctx.pass_test(TEST_NAME)


# =============================================================================
# Test 2: Persistent Path Routing
# =============================================================================


def test_persistent_path_routing(ctx: TestContext):
    """Check that persistent data uses correct paths.

    Bug: Code saves preferences to /memory/cache/ which matches the ephemeral
    StateBackend route, instead of /memory/ which uses persistent StoreBackend.
    """
    TEST_NAME = "persistent_path_routing"

    buggy_path = r"/memory/cache/prefs"
    correct_path_patterns = [
        r"/memory/prefs",
        r"/memory/user",
        r"/persistent/",
    ]

    has_buggy_path = re.search(buggy_path, ctx.source)
    has_correct_path = any(re.search(p, ctx.source) for p in correct_path_patterns)
    routes_buggy = re.search(r"/memory/cache/.*StateBackend", ctx.source, re.DOTALL)

    if not has_buggy_path or has_correct_path or not routes_buggy:
        ctx.pass_test(TEST_NAME)
    else:
        ctx.fail_test(
            TEST_NAME,
            "/memory/cache/ matches longer prefix than /memory/, "
            "so files there are ephemeral - use /memory/ directly or fix routes",
        )


# =============================================================================
# Test 3: Subagent Skills Inheritance
# =============================================================================


def test_subagent_skills(ctx: TestContext):
    """Check that subagents have explicit skills configuration.

    Bug: Custom subagents DON'T inherit main agent's skills.
    Only the general-purpose subagent does.
    """
    TEST_NAME = "subagent_skills_explicit"

    # Try execution-based check by patching create_deep_agent
    try:
        captured_calls = []
        original_create = None

        def capture_create(*args, **kwargs):
            captured_calls.append(kwargs)
            if original_create:
                return original_create(*args, **kwargs)
            return None

        import deepagents

        original_create = deepagents.create_deep_agent
        deepagents.create_deep_agent = capture_create

        try:
            # Clear cached import and reload
            if "agent_system" in sys.modules:
                del sys.modules["agent_system"]

            spec = importlib.util.spec_from_file_location("agent_system", ctx.module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "create_agent_system"):
                try:
                    module.create_agent_system()
                except Exception:
                    pass  # May fail without API keys

            # Analyze captured calls
            if captured_calls:
                result = _analyze_subagent_skills(captured_calls)
                if result:
                    ctx.fail_test(TEST_NAME, result)
                else:
                    ctx.pass_test(TEST_NAME)
                return

        finally:
            deepagents.create_deep_agent = original_create

    except ImportError:
        pass  # deepagents not available

    # Fall back to source check
    _check_subagent_skills_source(ctx)


def _analyze_subagent_skills(captured_calls: list) -> str | None:
    """Analyze captured create_deep_agent calls for skills issues.

    Returns error message if issues found, None if OK.
    """
    for kwargs in captured_calls:
        subagents = kwargs.get("subagents", [])
        main_skills = kwargs.get("skills", [])

        if not (subagents and main_skills):
            continue

        # Only check researcher — it explicitly needs doc skills per the task instruction
        missing = []
        for sub in subagents:
            if isinstance(sub, dict):
                name = sub.get("name", "unnamed")
                if name == "researcher" and ("skills" not in sub or not sub.get("skills")):
                    missing.append(name)

        if missing:
            return (
                f"custom subagents don't inherit main agent's skills - "
                f"specify skills explicitly (missing on: {', '.join(missing)})"
            )

    return None


def _check_subagent_skills_source(ctx: TestContext):
    """Source-based subagent skills check."""
    TEST_NAME = "subagent_skills_explicit"

    subagent_start = ctx.source.find("subagents=[")
    if subagent_start == -1:
        subagent_start = ctx.source.find("subagents = [")

    if subagent_start == -1:
        ctx.pass_test(TEST_NAME)
        return

    # Look at next 2000 chars for subagent definitions
    section = ctx.source[subagent_start : subagent_start + 2000]
    # Only check researcher — it explicitly needs doc skills per the task instruction
    researcher_match = re.search(
        r'"name"\s*:\s*"researcher".*?(?="name"|$)', section, re.DOTALL
    )
    if not researcher_match:
        ctx.pass_test(TEST_NAME)
    elif re.search(r'"skills"\s*:\s*\[', researcher_match.group()):
        ctx.pass_test(TEST_NAME)
    else:
        ctx.fail_test(
            TEST_NAME,
            "custom subagents don't inherit main agent's skills - "
            "specify skills explicitly (missing on: researcher)",
        )


# =============================================================================
# Test 4: Interrupt Requires Checkpointer
# =============================================================================


def test_interrupt_checkpointer(ctx: TestContext):
    """Check that interrupt_on has a checkpointer configured.

    Bug: Using interrupt_on without checkpointer silently fails -
    the interrupt won't actually pause execution.
    """
    TEST_NAME = "interrupt_has_checkpointer"

    has_interrupt = re.search(r"interrupt_on", ctx.source)
    has_checkpointer = re.search(r"checkpointer\s*=", ctx.source)

    if not has_interrupt:
        ctx.pass_test(TEST_NAME)
    elif has_checkpointer:
        ctx.pass_test(TEST_NAME)
    else:
        ctx.fail_test(
            TEST_NAME,
            "interrupt_on requires checkpointer on main agent - add checkpointer=MemorySaver()",
        )


# =============================================================================
# Main Test Runner
# =============================================================================


def run_tests(module_path: str) -> dict:
    """Run all tests against the module.

    Returns dict with test results: {passed: [], failed: [], error: str|None}
    """
    ctx = TestContext(module_path=module_path)

    if not ctx.load():
        return ctx.results

    # Run each test
    tests = [
        test_route_hierarchy,
        test_persistent_path_routing,
        test_subagent_skills,
        test_interrupt_checkpointer,
    ]

    for test_fn in tests:
        try:
            test_fn(ctx)
        except Exception as e:
            test_name = test_fn.__name__.replace("test_", "")
            ctx.fail_test(test_name, str(e))

    return ctx.results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_memory.py <path_to_agent_system.py>")
        sys.exit(1)

    module_path = sys.argv[1]
    results = run_tests(module_path)

    print(json.dumps(results, indent=2))

    if results["error"] or results["failed"]:
        sys.exit(1)
    sys.exit(0)
