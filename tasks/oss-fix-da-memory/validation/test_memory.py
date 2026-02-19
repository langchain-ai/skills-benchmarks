"""Pattern-based tests for deep agents memory/subagent fixes.

The broken code has bugs from multiple skill areas:

From da_memory:
1. CompositeBackend longest-prefix routing - /memory/cache/ matches more specific route
   than /memory/, so files saved there use StateBackend (ephemeral) not StoreBackend
2. Path choice for persistence - should use /memory/ directly, not /memory/cache/

From da_subagents:
3. Skill inheritance asymmetry - custom subagents DON'T inherit main agent's skills
   (only general-purpose subagent does)
4. Subagent interrupts require checkpointer - interrupt_on without checkpointer won't work

Tests verify correct patterns are present after fixing.
"""

import ast
import json
import re
import sys


def run_tests(module_path: str) -> dict:
    """Run tests against the module.

    Returns dict with test results.
    """
    results = {"passed": [], "failed": [], "error": None}

    try:
        with open(module_path) as f:
            source = f.read()
    except Exception as e:
        results["error"] = f"Failed to read file: {e}"
        return results

    try:
        ast.parse(source)
    except SyntaxError as e:
        results["error"] = f"Syntax error in file: {e}"
        return results

    # ========== da_memory bugs ==========

    # Test 1: Persistent data should NOT be saved under a more-specific ephemeral route
    # The bug: /memory/cache/ matches longer prefix than /memory/, so it's ephemeral
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
        # Buggy: /memory/cache/ -> StateBackend (ephemeral)
        # Fixed: /memory/cache/ removed OR -> StoreBackend
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

    # Test 2: Composite backend route understanding
    # Check if the routes make sense (no ephemeral under persistent)
    try:
        # Find route definitions
        composite_routes = re.search(r"routes\s*=\s*\{([^}]+)\}", source, re.DOTALL)

        if composite_routes:
            routes_content = composite_routes.group(1)
            # Check for nested ephemeral under persistent
            has_nested_ephemeral = (
                "StateBackend" in routes_content
                and "/memory/" in routes_content
                and "/memory/cache/" in routes_content
            )

            if not has_nested_ephemeral:
                results["passed"].append("route_hierarchy_correct")
            else:
                # Check if the nested one is also StoreBackend
                if re.search(r"/memory/cache/.*StoreBackend", routes_content):
                    results["passed"].append("route_hierarchy_correct")
                else:
                    results["failed"].append(
                        "route_hierarchy_correct: longer prefix routes take precedence - "
                        "/memory/cache/ overrides /memory/, making cache ephemeral"
                    )
        else:
            results["passed"].append("route_hierarchy_correct")
    except Exception as e:
        results["failed"].append(f"route_hierarchy_correct: {e}")

    # ========== da_subagents bugs ==========

    # Test 3: Custom subagents need explicit skills (don't inherit)
    try:
        # Find subagent definitions
        subagent_pattern = r"subagents\s*=\s*\[([^\]]+)\]"
        subagents_match = re.search(subagent_pattern, source, re.DOTALL)

        if subagents_match:
            subagents_content = subagents_match.group(1)

            # Check if subagents have skills specified
            # Looking for "skills": [...] in subagent definitions
            skills_specs = re.findall(r'"skills"\s*:\s*\[', subagents_content)

            # Each custom subagent that needs skills should have them specified
            has_explicit_skills = len(skills_specs) > 0

            if has_explicit_skills:
                results["passed"].append("subagent_skills_explicit")
            else:
                results["failed"].append(
                    "subagent_skills_explicit: custom subagents don't inherit "
                    "main agent's skills - specify skills explicitly"
                )
        else:
            results["passed"].append("subagent_skills_explicit")
    except Exception as e:
        results["failed"].append(f"subagent_skills_explicit: {e}")

    # Test 4: Subagent interrupt_on requires checkpointer on main agent
    try:
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
    except Exception as e:
        results["failed"].append(f"interrupt_has_checkpointer: {e}")

    return results


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
