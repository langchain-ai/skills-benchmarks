"""Behavioral tests for deep agents memory/subagent fixes.

These tests execute the code and verify actual behavior -- not just source patterns.
We patch create_deep_agent to capture the config, then test:
1. Backend routing: does the prefs path resolve to persistent storage?
2. Subagent skills: does the researcher subagent have explicit skills?
3. Interrupt + checkpointer: is checkpointer configured when interrupt_on is used?

Usage: TestRunner pattern with runner.load_module() for module import.
"""

import ast
import os
import re
import sys

from scaffold.python.validation.runner import TestRunner

# Global cache for the patched module + captured config
_cached_result = None


def _require_module_and_config(runner: TestRunner):
    """Load module with patched create_deep_agent and return (module, source, captured_config).

    Cached globally so the patching + import only happens once.
    Returns (None, None, None) on failure.
    """
    global _cached_result
    if _cached_result is not None:
        return _cached_result

    artifact_path = runner.artifacts[0]
    source = runner.read(artifact_path)
    if not source:
        runner.failed(f"Failed to read file: {artifact_path}")
        _cached_result = (None, None, None)
        return _cached_result

    module_dir = os.path.dirname(os.path.abspath(artifact_path))
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)

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
            import importlib.util

            if "agent_system" in sys.modules:
                del sys.modules["agent_system"]
            spec = importlib.util.spec_from_file_location("agent_system", artifact_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "create_agent_system"):
                module.create_agent_system()
        finally:
            deepagents.create_deep_agent = original
    except Exception as e:
        runner.failed(f"import error ({artifact_path}): {e}")
        _cached_result = (None, None, None)
        return _cached_result

    _cached_result = (module, source, captured)
    return _cached_result


# =============================================================================
# Check 1: Prefs path resolves to persistent backend
# =============================================================================


def _resolve_backend(path, sorted_routes, default_backend):
    """Simulate CompositeBackend longest-prefix routing."""
    for prefix, backend in sorted_routes:
        if path.startswith(prefix):
            return type(backend).__name__, prefix
    return type(default_backend).__name__, "(default)"


def _check_prefs_persist_source(runner: TestRunner, source):
    """Source-based fallback for prefs persistence check."""
    TEST_NAME = "prefs_use_persistent_storage"

    pref_paths = set()
    for match in re.finditer(r"(/memory/[^\s\"'{}]*prefs[^\s\"'{}]*)", source):
        pref_paths.add(match.group(1))

    if not pref_paths:
        runner.passed(TEST_NAME)
        return

    # Extract ephemeral routes
    ephemeral_prefixes = set()
    persistent_prefixes = set()
    routes_match = re.search(r"routes\s*=\s*\{([^}]+)\}", source, re.DOTALL)
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
            runner.failed(
                f"{TEST_NAME}: "
                f"'{pref_path}' resolves to ephemeral route '{longest}' "
                f"(longest-prefix match) — preferences lost on restart"
            )
            return

    runner.passed(TEST_NAME)


def check_prefs_use_persistent_storage(runner: TestRunner):
    """Verify preferences path resolves to persistent (StoreBackend) storage.

    Tests the actual backend routing by instantiating the backend_factory
    from the code and checking what backend a prefs path resolves to.
    Falls back to source analysis if execution-based check isn't possible.
    """
    module, source, captured_config = _require_module_and_config(runner)
    if module is None:
        return

    # Try behavioral: instantiate the backend and test routing
    backend_fn = captured_config.get("backend")
    if callable(backend_fn):
        try:
            from langgraph.store.memory import InMemoryStore

            backend = backend_fn(InMemoryStore())
            if hasattr(backend, "sorted_routes"):
                # Extract the prefs path from source
                pref_paths = re.findall(r"(/memory/[^\s\"'{}]*prefs[^\s\"'{}]*)", source)
                if not pref_paths:
                    runner.passed("prefs_use_persistent_storage")
                    return

                for pref_path in pref_paths:
                    backend_type, matched_prefix = _resolve_backend(
                        pref_path, backend.sorted_routes, backend.default
                    )
                    if "State" in backend_type:
                        runner.failed(
                            f"prefs_use_persistent_storage: "
                            f"'{pref_path}' routes to {backend_type} via '{matched_prefix}' "
                            f"(ephemeral) — preferences lost on restart"
                        )
                        return
                runner.passed("prefs_use_persistent_storage")
                return
        except Exception:
            pass  # Fall through to source-based check

    # Source-based fallback
    _check_prefs_persist_source(runner, source)


# =============================================================================
# Check 2: Subagent skills
# =============================================================================


def _check_subagent_skills_source(runner: TestRunner, source):
    """Source-based subagent skills check."""
    TEST_NAME = "subagent_skills_explicit"

    subagent_start = source.find("subagents=[")
    if subagent_start == -1:
        subagent_start = source.find("subagents = [")
    if subagent_start == -1:
        runner.passed(TEST_NAME)
        return

    section = source[subagent_start : subagent_start + 2000]
    researcher_match = re.search(r'"name"\s*:\s*"researcher".*?(?="name"|$)', section, re.DOTALL)
    if not researcher_match:
        runner.passed(TEST_NAME)
    elif re.search(r'"skills"\s*:\s*\[', researcher_match.group()):
        runner.passed(TEST_NAME)
    else:
        runner.failed(
            f"{TEST_NAME}: "
            "researcher subagent missing 'skills' — custom subagents "
            "don't inherit main agent's skills, specify explicitly"
        )


def check_subagent_skills_explicit(runner: TestRunner):
    """Verify researcher subagent has explicit skills configuration.

    Custom subagents don't inherit the main agent's skills -- they need
    skills specified explicitly in their config dict.
    """
    module, source, captured_config = _require_module_and_config(runner)
    if module is None:
        return

    subagents = captured_config.get("subagents", [])
    main_skills = captured_config.get("skills", [])

    # Behavioral check: inspect captured config
    if subagents and main_skills:
        for sub in subagents:
            if isinstance(sub, dict) and sub.get("name") == "researcher":
                if "skills" in sub and sub["skills"]:
                    runner.passed("subagent_skills_explicit")
                else:
                    runner.failed(
                        "subagent_skills_explicit: "
                        "researcher subagent missing 'skills' — custom subagents "
                        "don't inherit main agent's skills, specify explicitly"
                    )
                return
        # No researcher found
        runner.passed("subagent_skills_explicit")
        return

    # Source-based fallback
    _check_subagent_skills_source(runner, source)


# =============================================================================
# Check 3: Interrupt requires checkpointer
# =============================================================================


def check_interrupt_has_checkpointer(runner: TestRunner):
    """Verify interrupt_on has a checkpointer configured.

    Without a checkpointer, interrupt_on silently does nothing -- the agent
    won't actually pause for human approval.
    """
    module, source, captured_config = _require_module_and_config(runner)
    if module is None:
        return

    # Behavioral check: inspect captured config
    has_interrupt = False
    for sub in captured_config.get("subagents", []):
        if isinstance(sub, dict) and sub.get("interrupt_on"):
            has_interrupt = True
            break

    has_checkpointer = "checkpointer" in captured_config

    if has_interrupt or re.search(r"interrupt_on", source):
        if has_checkpointer or re.search(r"checkpointer\s*=", source):
            runner.passed("interrupt_has_checkpointer")
        else:
            runner.failed(
                "interrupt_has_checkpointer: "
                "interrupt_on requires checkpointer on main agent — add checkpointer=MemorySaver()"
            )
    else:
        runner.passed("interrupt_has_checkpointer")


# =============================================================================
# Check 4: AST verification -- code was actually changed
# =============================================================================


def check_ast_has_checkpointer_kwarg(runner: TestRunner):
    """Verify key fixes are present in the source via AST inspection.

    These complement the behavioral checks -- the behavioral tests verify
    the config is correct, these verify the code was actually modified.
    """
    module, source, captured_config = _require_module_and_config(runner)
    if module is None:
        return

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return  # Already caught by load

    # Check: create_deep_agent called with checkpointer keyword
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
                    runner.passed("ast_has_checkpointer_kwarg")
                else:
                    runner.failed(
                        "ast_has_checkpointer_kwarg: "
                        "create_deep_agent call missing checkpointer= keyword"
                    )
                return

    # If we didn't find create_deep_agent call at all, that's also a problem
    runner.failed("ast_has_checkpointer_kwarg: create_deep_agent call not found in source")


if __name__ == "__main__":
    TestRunner.run(
        [
            check_prefs_use_persistent_storage,
            check_subagent_skills_explicit,
            check_interrupt_has_checkpointer,
            check_ast_has_checkpointer_kwarg,
        ]
    )
