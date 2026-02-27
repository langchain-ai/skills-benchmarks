"""Behavioral tests for deep agents memory/subagent fixes.

These tests execute the code and verify actual behavior — not just source patterns.
We patch create_deep_agent to capture the config, then test:
1. Backend routing: does the prefs path resolve to persistent storage?
2. Subagent skills: does the researcher subagent have explicit skills?
3. Interrupt + checkpointer: is checkpointer configured when interrupt_on is used?

Usage: python test_memory.py <path_to_agent_system.py>
"""

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
    captured_config: dict = field(default_factory=dict)
    results: dict = field(default_factory=lambda: {"passed": [], "failed": [], "error": None})

    def load(self) -> bool:
        """Load source, import module with patched create_deep_agent."""
        module_dir = os.path.dirname(os.path.abspath(self.module_path))
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)

        try:
            with open(self.module_path) as f:
                self.source = f.read()
        except Exception as e:
            self.results["error"] = f"Failed to read file: {e}"
            return False

        # Patch create_deep_agent to capture kwargs without needing API keys
        try:
            import deepagents

            original = deepagents.create_deep_agent
            captured = {}

            def capture_create(*args, **kwargs):
                captured.update(kwargs)
                # Return a mock that won't crash
                return type("MockAgent", (), {"invoke": lambda *a, **k: {}})()

            deepagents.create_deep_agent = capture_create
            try:
                if "agent_system" in sys.modules:
                    del sys.modules["agent_system"]
                spec = importlib.util.spec_from_file_location("agent_system", self.module_path)
                self.module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.module)
                if hasattr(self.module, "create_agent_system"):
                    self.module.create_agent_system()
                self.captured_config = captured
            finally:
                deepagents.create_deep_agent = original
        except Exception as e:
            self.results["error"] = f"Failed to import module: {e}"
            return False

        return True

    def pass_test(self, name: str):
        self.results["passed"].append(name)

    def fail_test(self, name: str, reason: str):
        self.results["failed"].append(f"{name}: {reason}")


# =============================================================================
# Test 1: Prefs path resolves to persistent backend
# =============================================================================


def _resolve_backend(path, sorted_routes, default_backend):
    """Simulate CompositeBackend longest-prefix routing."""
    for prefix, backend in sorted_routes:
        if path.startswith(prefix):
            return type(backend).__name__, prefix
    return type(default_backend).__name__, "(default)"


def test_prefs_persist(ctx: TestContext):
    """Verify preferences path resolves to persistent (StoreBackend) storage.

    Tests the actual backend routing by instantiating the backend_factory
    from the code and checking what backend a prefs path resolves to.
    Falls back to source analysis if execution-based check isn't possible.
    """
    TEST_NAME = "prefs_use_persistent_storage"

    # Try behavioral: instantiate the backend and test routing
    backend_fn = ctx.captured_config.get("backend")
    if callable(backend_fn):
        try:
            from langgraph.store.memory import InMemoryStore

            backend = backend_fn(InMemoryStore())
            if hasattr(backend, "sorted_routes"):
                # Extract the prefs path from source
                pref_paths = re.findall(
                    r"(/memory/[^\s\"'{}]*prefs[^\s\"'{}]*)", ctx.source
                )
                if not pref_paths:
                    ctx.pass_test(TEST_NAME)
                    return

                for pref_path in pref_paths:
                    backend_type, matched_prefix = _resolve_backend(
                        pref_path, backend.sorted_routes, backend.default
                    )
                    if "State" in backend_type:
                        ctx.fail_test(
                            TEST_NAME,
                            f"'{pref_path}' routes to {backend_type} via '{matched_prefix}' "
                            f"(ephemeral) — preferences lost on restart",
                        )
                        return
                ctx.pass_test(TEST_NAME)
                return
        except Exception:
            pass  # Fall through to source-based check

    # Source-based fallback
    _check_prefs_persist_source(ctx)


def _check_prefs_persist_source(ctx: TestContext):
    """Source-based fallback for prefs persistence check."""
    TEST_NAME = "prefs_use_persistent_storage"

    pref_paths = set()
    for match in re.finditer(r"(/memory/[^\s\"'{}]*prefs[^\s\"'{}]*)", ctx.source):
        pref_paths.add(match.group(1))

    if not pref_paths:
        ctx.pass_test(TEST_NAME)
        return

    # Extract ephemeral routes
    ephemeral_prefixes = set()
    persistent_prefixes = set()
    routes_match = re.search(r"routes\s*=\s*\{([^}]+)\}", ctx.source, re.DOTALL)
    if routes_match:
        for m in re.finditer(r'["\']([^"\']+)["\']\s*:\s*StateBackend', routes_match.group(1)):
            ephemeral_prefixes.add(m.group(1))
        for m in re.finditer(r'["\']([^"\']+)["\']\s*:\s*StoreBackend', routes_match.group(1)):
            persistent_prefixes.add(m.group(1))

    for pref_path in pref_paths:
        all_matches = [
            p for p in (ephemeral_prefixes | persistent_prefixes) if pref_path.startswith(p)
        ]
        if not all_matches:
            continue
        longest = max(all_matches, key=len)
        if longest in ephemeral_prefixes:
            ctx.fail_test(
                TEST_NAME,
                f"'{pref_path}' resolves to ephemeral route '{longest}' "
                f"(longest-prefix match) — preferences lost on restart",
            )
            return

    ctx.pass_test(TEST_NAME)


# =============================================================================
# Test 2: Subagent skills
# =============================================================================


def test_subagent_skills(ctx: TestContext):
    """Verify researcher subagent has explicit skills configuration.

    Custom subagents don't inherit the main agent's skills — they need
    skills specified explicitly in their config dict.
    """
    TEST_NAME = "subagent_skills_explicit"

    subagents = ctx.captured_config.get("subagents", [])
    main_skills = ctx.captured_config.get("skills", [])

    # Behavioral check: inspect captured config
    if subagents and main_skills:
        for sub in subagents:
            if isinstance(sub, dict) and sub.get("name") == "researcher":
                if "skills" in sub and sub["skills"]:
                    ctx.pass_test(TEST_NAME)
                else:
                    ctx.fail_test(
                        TEST_NAME,
                        "researcher subagent missing 'skills' — custom subagents "
                        "don't inherit main agent's skills, specify explicitly",
                    )
                return
        # No researcher found
        ctx.pass_test(TEST_NAME)
        return

    # Source-based fallback
    _check_subagent_skills_source(ctx)


def _check_subagent_skills_source(ctx: TestContext):
    """Source-based subagent skills check."""
    TEST_NAME = "subagent_skills_explicit"

    subagent_start = ctx.source.find("subagents=[")
    if subagent_start == -1:
        subagent_start = ctx.source.find("subagents = [")
    if subagent_start == -1:
        ctx.pass_test(TEST_NAME)
        return

    section = ctx.source[subagent_start : subagent_start + 2000]
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
            "researcher subagent missing 'skills' — custom subagents "
            "don't inherit main agent's skills, specify explicitly",
        )


# =============================================================================
# Test 3: Interrupt requires checkpointer
# =============================================================================


def test_interrupt_checkpointer(ctx: TestContext):
    """Verify interrupt_on has a checkpointer configured.

    Without a checkpointer, interrupt_on silently does nothing — the agent
    won't actually pause for human approval.
    """
    TEST_NAME = "interrupt_has_checkpointer"

    # Behavioral check: inspect captured config
    has_interrupt = False
    for sub in ctx.captured_config.get("subagents", []):
        if isinstance(sub, dict) and sub.get("interrupt_on"):
            has_interrupt = True
            break

    has_checkpointer = "checkpointer" in ctx.captured_config

    if has_interrupt or re.search(r"interrupt_on", ctx.source):
        if has_checkpointer or re.search(r"checkpointer\s*=", ctx.source):
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                "interrupt_on requires checkpointer on main agent — "
                "add checkpointer=MemorySaver()",
            )
    else:
        ctx.pass_test(TEST_NAME)


# =============================================================================
# Test 4: AST verification — code was actually changed
# =============================================================================


def test_ast_checks(ctx: TestContext):
    """Verify key fixes are present in the source via AST inspection.

    These complement the behavioral checks — the behavioral tests verify
    the config is correct, these verify the code was actually modified.
    """
    import ast

    try:
        tree = ast.parse(ctx.source)
    except SyntaxError:
        return  # Already caught by load()

    # Check 1: create_deep_agent called with checkpointer keyword
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = ""
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name == "create_deep_agent":
                kw_names = [kw.arg for kw in node.keywords]
                if "checkpointer" in kw_names:
                    ctx.pass_test("ast_has_checkpointer_kwarg")
                else:
                    ctx.fail_test(
                        "ast_has_checkpointer_kwarg",
                        "create_deep_agent call missing checkpointer= keyword",
                    )
                break



# =============================================================================
# Main Test Runner
# =============================================================================


def run_tests(module_path: str) -> dict:
    ctx = TestContext(module_path=module_path)

    tests = [
        test_prefs_persist,
        test_subagent_skills,
        test_interrupt_checkpointer,
        test_ast_checks,
    ]

    if not ctx.load():
        for test_fn in tests:
            test_name = test_fn.__name__.replace("test_", "")
            ctx.fail_test(test_name, f"import failed: {ctx.results['error']}")
        return ctx.results

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

    results = run_tests(sys.argv[1])
    print(json.dumps(results, indent=2))
    sys.exit(1 if results["error"] or results["failed"] else 0)
