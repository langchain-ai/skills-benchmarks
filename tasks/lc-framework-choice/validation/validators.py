"""Function-based validators for lc-framework-choice task.

Tests whether Claude picks the right framework for each component:
- qa_agent.py: simple agent → create_agent (NOT create_react_agent from LangGraph)
- approval_pipeline.py: deterministic routing → LangGraph StateGraph
- middleware_agent.py: hooks/middleware → create_agent or create_deep_agent (NOT LangGraph)
- research_assistant.py: sub-agents + planning → create_deep_agent
"""

import ast
from pathlib import Path

from scaffold.python.utils import evaluate_with_schema, run_python_in_docker
from scaffold.python.validation import validate_skill_invoked


def validate_qa_agent(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Simple agent should use create_agent, not create_react_agent from LangGraph."""
    passed, failed = [], []
    path = test_dir / "qa_agent.py"

    if not path.exists():
        return [], ["QA Agent: qa_agent.py not created"]

    content = path.read_text()
    passed.append("QA Agent: qa_agent.py created")

    try:
        ast.parse(content)
        passed.append("QA Agent: valid syntax")
    except SyntaxError as e:
        return passed, failed + [f"QA Agent: syntax error line {e.lineno}"]

    if "from langchain.agents import create_agent" in content:
        passed.append("QA Agent: correctly uses create_agent")
    else:
        failed.append("QA Agent: missing create_agent from langchain.agents")

    if "from langgraph.prebuilt import create_react_agent" in content:
        failed.append("QA Agent: uses create_react_agent from LangGraph (should use create_agent for simple agent)")

    if "StateGraph" in content:
        failed.append("QA Agent: uses LangGraph StateGraph (overkill for simple react agent)")

    return passed, failed


def validate_approval_pipeline(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Deterministic routing workflow should use LangGraph StateGraph."""
    passed, failed = [], []
    path = test_dir / "approval_pipeline.py"

    if not path.exists():
        return [], ["Approval Pipeline: approval_pipeline.py not created"]

    content = path.read_text()
    passed.append("Approval Pipeline: approval_pipeline.py created")

    try:
        ast.parse(content)
        passed.append("Approval Pipeline: valid syntax")
    except SyntaxError as e:
        return passed, failed + [f"Approval Pipeline: syntax error line {e.lineno}"]

    if "StateGraph" in content:
        passed.append("Approval Pipeline: correctly uses LangGraph StateGraph for deterministic routing")
    else:
        failed.append("Approval Pipeline: missing LangGraph StateGraph (required for deterministic branching)")

    if "add_conditional_edges" in content or "add_edge" in content:
        passed.append("Approval Pipeline: uses explicit edge routing")

    return passed, failed


def validate_middleware_agent(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Middleware/hooks should use create_agent or create_deep_agent — NOT LangGraph."""
    passed, failed = [], []
    path = test_dir / "middleware_agent.py"

    if not path.exists():
        return [], ["Middleware Agent: middleware_agent.py not created"]

    content = path.read_text()
    passed.append("Middleware Agent: middleware_agent.py created")

    try:
        ast.parse(content)
        passed.append("Middleware Agent: valid syntax")
    except SyntaxError as e:
        return passed, failed + [f"Middleware Agent: syntax error line {e.lineno}"]

    uses_create_agent = "create_agent" in content
    uses_deep_agent = "create_deep_agent" in content
    uses_langgraph = "StateGraph" in content

    if uses_langgraph:
        failed.append("Middleware Agent: uses LangGraph StateGraph (middleware/hooks are not a LangGraph concept)")

    if uses_create_agent or uses_deep_agent:
        which = "create_agent" if uses_create_agent else "create_deep_agent"
        passed.append(f"Middleware Agent: correctly uses {which} for hook/middleware pattern")
    elif not uses_langgraph:
        failed.append("Middleware Agent: missing create_agent or create_deep_agent")

    return passed, failed


def validate_research_assistant(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Open-ended research with sub-agents should use create_deep_agent."""
    passed, failed = [], []
    path = test_dir / "research_assistant.py"

    if not path.exists():
        return [], ["Research Assistant: research_assistant.py not created"]

    content = path.read_text()
    passed.append("Research Assistant: research_assistant.py created")

    try:
        ast.parse(content)
        passed.append("Research Assistant: valid syntax")
    except SyntaxError as e:
        return passed, failed + [f"Research Assistant: syntax error line {e.lineno}"]

    if "create_deep_agent" in content:
        passed.append("Research Assistant: correctly uses create_deep_agent for sub-agent orchestration")
    else:
        failed.append("Research Assistant: missing create_deep_agent (required for sub-agent planning)")

    return passed, failed


def validate_personal_assistant(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Built-in planning + memory management should use create_deep_agent."""
    passed, failed = [], []
    path = test_dir / "personal_assistant.py"

    if not path.exists():
        return [], ["Personal Assistant: personal_assistant.py not created"]

    content = path.read_text()
    passed.append("Personal Assistant: personal_assistant.py created")

    try:
        ast.parse(content)
        passed.append("Personal Assistant: valid syntax")
    except SyntaxError as e:
        return passed, failed + [f"Personal Assistant: syntax error line {e.lineno}"]

    if "create_deep_agent" in content:
        passed.append("Personal Assistant: correctly uses create_deep_agent for built-in planning + memory")
    else:
        failed.append("Personal Assistant: missing create_deep_agent (required for built-in planning and memory management)")

    if "StateGraph" in content and "create_deep_agent" not in content:
        failed.append("Personal Assistant: uses LangGraph StateGraph instead of create_deep_agent for memory management")

    return passed, failed


def validate_skill_usage(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Track skill invocation (informational, doesn't fail)."""
    return validate_skill_invoked(outputs, "framework-selection", required=False)


def validate_metrics(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Collect turn/duration metrics (always passes)."""
    events = outputs.get("events", {}) if outputs else {}
    return [
        f"Turns: {events.get('num_turns', 0) or 0}",
        f"Duration: {events.get('duration_seconds', 0) or 0:.0f}s",
        f"Tool calls: {len(events.get('tool_calls', []))}",
    ], []


VALIDATORS = [
    validate_skill_usage,
    validate_qa_agent,
    validate_approval_pipeline,
    validate_middleware_agent,
    validate_research_assistant,
    validate_personal_assistant,
    validate_metrics,
]
