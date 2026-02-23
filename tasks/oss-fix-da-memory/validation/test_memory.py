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
import json
import re
import sys
import importlib.util
import os


def run_tests(module_path: str) -> dict:
    """Run execution-based tests against the module.

    Returns dict with test results.
    """
    results = {"passed": [], "failed": [], "error": None}

    # Add module directory to path for imports
    module_dir = os.path.dirname(os.path.abspath(module_path))
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)

    # Read source for pattern analysis (backup)
    try:
        with open(module_path) as f:
            source = f.read()
    except Exception as e:
        results["error"] = f"Failed to read file: {e}"
        return results

    # Parse AST for structure analysis
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        results["error"] = f"Syntax error in file: {e}"
        return results

    # Try to import and test execution
    try:
        spec = importlib.util.spec_from_file_location("agent_system", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        has_module = True
    except Exception as e:
        # Module failed to import - fall back to pattern checks
        has_module = False

    # ========== Test 1: Route hierarchy - execution-based ==========
    # Bug: /memory/cache/ matches longer prefix than /memory/, making it ephemeral
    try:
        if has_module and hasattr(module, 'create_agent_system'):
            # Try to create agent and check backend configuration
            try:
                agent = module.create_agent_system()

                # Check if agent has backend with routes
                backend = getattr(agent, 'backend', None)
                if backend is None and hasattr(agent, '_backend'):
                    backend = agent._backend

                if backend and hasattr(backend, 'sorted_routes'):
                    # Check route order - longer prefixes should come first
                    routes = backend.sorted_routes
                    has_nested_ephemeral = False

                    for prefix, backend_instance in routes:
                        backend_type = type(backend_instance).__name__
                        if '/memory/cache/' in prefix and 'State' in backend_type:
                            has_nested_ephemeral = True
                            break

                    if has_nested_ephemeral:
                        results["failed"].append(
                            "route_hierarchy_correct: longer prefix routes take precedence - "
                            "/memory/cache/ overrides /memory/, making cache ephemeral"
                        )
                    else:
                        results["passed"].append("route_hierarchy_correct")
                else:
                    # Fall back to source analysis
                    _check_route_hierarchy_source(source, results)
            except Exception as e:
                # Agent creation failed - fall back to source
                _check_route_hierarchy_source(source, results)
        else:
            _check_route_hierarchy_source(source, results)
    except Exception as e:
        results["failed"].append(f"route_hierarchy_correct: {e}")

    # ========== Test 2: Persistent path routing ==========
    try:
        # Check if preferences are saved to /memory/cache/ (buggy) or /memory/ (correct)
        buggy_path = r"/memory/cache/prefs"
        correct_path_patterns = [
            r"/memory/prefs",  # Direct under /memory/
            r"/memory/user",  # Or similar persistent path
            r"/persistent/",  # Or renamed route
        ]

        has_buggy_path = re.search(buggy_path, source)
        has_correct_path = any(re.search(pattern, source) for pattern in correct_path_patterns)

        # Also check if the routes themselves were fixed
        routes_buggy = re.search(r"/memory/cache/.*StateBackend", source, re.DOTALL)

        if not has_buggy_path or has_correct_path:
            results["passed"].append("persistent_path_routing")
        elif not routes_buggy:
            results["passed"].append("persistent_path_routing")
        else:
            results["failed"].append(
                "persistent_path_routing: /memory/cache/ matches longer prefix than "
                "/memory/, so files there are ephemeral - use /memory/ directly or fix routes"
            )
    except Exception as e:
        results["failed"].append(f"persistent_path_routing: {e}")

    # ========== Test 3: Subagent skill inheritance ==========
    # Always use source-based check since deepagents compiles to LangGraph
    # and doesn't expose subagent config as attributes
    try:
        _check_subagent_skills_source(source, results)
    except Exception as e:
        results["failed"].append(f"subagent_skills_explicit: {e}")

    # ========== Test 4: Interrupt requires checkpointer ==========
    # Always use source-based check since deepagents compiles to LangGraph
    try:
        _check_interrupt_checkpointer_source(source, results)
    except Exception as e:
        results["failed"].append(f"interrupt_has_checkpointer: {e}")

    return results


def _check_route_hierarchy_source(source: str, results: dict):
    """Fall back to source-based route hierarchy check."""
    composite_routes = re.search(r"routes\s*=\s*\{([^}]+)\}", source, re.DOTALL)

    if composite_routes:
        routes_content = composite_routes.group(1)
        has_nested_ephemeral = (
            "StateBackend" in routes_content
            and "/memory/" in routes_content
            and "/memory/cache/" in routes_content
        )

        if not has_nested_ephemeral:
            results["passed"].append("route_hierarchy_correct")
        else:
            if re.search(r"/memory/cache/.*StoreBackend", routes_content):
                results["passed"].append("route_hierarchy_correct")
            else:
                results["failed"].append(
                    "route_hierarchy_correct: longer prefix routes take precedence - "
                    "/memory/cache/ overrides /memory/, making cache ephemeral"
                )
    else:
        results["passed"].append("route_hierarchy_correct")


def _check_subagent_skills_source(source: str, results: dict):
    """Fall back to source-based subagent skills check."""
    # Find subagents= and extract until the matching closing bracket
    # Use a simpler approach: find subagents= and look for "skills" nearby
    subagent_start = source.find('subagents=[')
    if subagent_start == -1:
        subagent_start = source.find('subagents = [')

    if subagent_start != -1:
        # Find the section from subagents to the end of that argument
        # Look at the next 2000 chars which should contain all subagent defs
        subagents_section = source[subagent_start:subagent_start + 2000]

        # Count subagent blocks by looking for "name":
        subagent_count = len(re.findall(r'"name"\s*:', subagents_section))

        # Count explicit skills specifications
        skills_specs = len(re.findall(r'"skills"\s*:\s*\[', subagents_section))

        # Each custom subagent should have skills
        if subagent_count > 0 and skills_specs == 0:
            results["failed"].append(
                "subagent_skills_explicit: custom subagents don't inherit "
                "main agent's skills - specify skills explicitly"
            )
        elif skills_specs >= subagent_count:
            results["passed"].append("subagent_skills_explicit")
        else:
            # Some subagents have skills, some don't
            results["failed"].append(
                "subagent_skills_explicit: custom subagents don't inherit "
                "main agent's skills - specify skills explicitly"
            )
    else:
        results["passed"].append("subagent_skills_explicit")


def _check_interrupt_checkpointer_source(source: str, results: dict):
    """Fall back to source-based interrupt checkpointer check."""
    has_interrupt_on = re.search(r"interrupt_on", source)
    has_checkpointer = re.search(r"checkpointer\s*=", source)

    if has_interrupt_on:
        if has_checkpointer:
            results["passed"].append("interrupt_has_checkpointer")
        else:
            results["failed"].append(
                "interrupt_has_checkpointer: interrupt_on requires checkpointer "
                "on main agent - add checkpointer=MemorySaver()"
            )
    else:
        results["passed"].append("interrupt_has_checkpointer")


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
