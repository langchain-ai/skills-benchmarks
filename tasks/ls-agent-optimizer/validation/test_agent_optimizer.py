"""Test script for ls-agent-optimizer validation.

Checks that fixes.md recalls each planted issue and that the two
highest-priority fixes were applied to the agent harness files.
Runs inside Docker via make_execution_validator.

Evidence correlation: upload_traces regenerates run IDs, but the old->new
root-run mapping is available via runner.context["trace_id_map"]. Each
planted session also contains a unique token (order numbers, error codes,
ticket/case IDs) so citations can be string-matched deterministically.
"""

from scaffold.python.utils import evaluate_with_schema
from scaffold.python.validation.runner import TestRunner

# Original root-run IDs from data/trace_*.jsonl (keys of trace_id_map)
CLAIMS_SUCCESS_ROOTS = [
    "a0a0a0a0-0000-4000-8000-000000000001",
    "a0a0a0a0-0000-4000-8000-000000000002",
]

# Unique tokens planted in each issue's sessions
CLAIMS_SUCCESS_TOKENS = ["pmt-5521", "sub-9114", "ref-8830", "mia.torres"]
HALLUCINATED_TOOL_TOKENS = ["ord-7741", "ord-2293"]
KB_CATEGORY_TOKENS = ["tkt-4452", "tkt-6619", "tkt-7705"]
PDF_REQUEST_TOKENS = ["case-1102", "case-3358", "case-9876"]

# The misleading sentence planted in the search_kb docstring
MISLEADING_DOCSTRING = "Leave it out to search all categories"


def _new_run_ids(runner: TestRunner, original_ids: list[str]) -> list[str]:
    """Map planted root-run IDs to the IDs they got after upload."""
    trace_id_map = runner.context.get("trace_id_map", {}) or {}
    return [trace_id_map[old] for old in original_ids if trace_id_map.get(old)]


def check_found_success_after_failure(runner: TestRunner):
    """fixes.md flags the claims-success-after-failed-tool-call pattern with evidence."""
    fixes = runner.read(runner.artifacts[0]).lower()
    claim_words = ["claim", "said done", "says done", "reports success", "success", "all set"]
    failure_words = ["fail", "error", "timeout", "rejected"]
    pattern_found = any(w in fixes for w in claim_words) and any(w in fixes for w in failure_words)
    if not pattern_found:
        runner.failed("fixes.md does not describe the success-claim-after-failure pattern")
        return

    new_ids = [i.lower() for i in _new_run_ids(runner, CLAIMS_SUCCESS_ROOTS)]
    evidence = [t for t in CLAIMS_SUCCESS_TOKENS + new_ids if t in fixes]
    if evidence:
        runner.passed(f"found success-after-failure pattern with evidence: {evidence}")
    else:
        runner.failed(
            "success-after-failure pattern described but no evidence cited "
            f"(expected a run ID from {new_ids} or a token from {CLAIMS_SUCCESS_TOKENS})"
        )


def check_found_hallucinated_tool(runner: TestRunner):
    """fixes.md flags lookup_order_status AND the stale reference was removed from the prompt."""
    fixes = runner.read(runner.artifacts[0]).lower()
    if "lookup_order_status" not in fixes:
        runner.failed("fixes.md does not mention the hallucinated lookup_order_status tool")
        return
    runner.passed("fixes.md flags the hallucinated lookup_order_status tool")

    # Two valid fixes: remove the stale reference from the prompt, OR implement
    # the missing tool so the reference is no longer stale. Accept either.
    prompt = runner.read("agent/system_prompt.md")
    if not prompt:
        runner.failed("agent/system_prompt.md missing or empty")
        return
    tools_src = runner.read("agent/tools.py")
    if "def lookup_order_status" in tools_src:
        runner.passed("lookup_order_status implemented in agent/tools.py (valid alternative fix)")
    elif "lookup_order_status" in prompt:
        runner.failed("stale lookup_order_status reference neither removed from system_prompt.md nor implemented in tools.py")
    else:
        runner.passed("stale lookup_order_status reference removed from agent/system_prompt.md")


def check_found_tool_desc_bug(runner: TestRunner):
    """fixes.md flags the search_kb category docstring AND tools.py was corrected."""
    fixes = runner.read(runner.artifacts[0]).lower()
    if "search_kb" in fixes and "category" in fixes:
        runner.passed("fixes.md flags the search_kb category docstring bug")
    else:
        runner.failed("fixes.md does not flag the search_kb category docstring bug")
        return

    tools = runner.read("agent/tools.py")
    if not tools:
        runner.failed("agent/tools.py missing or empty")
        return
    if MISLEADING_DOCSTRING in tools:
        runner.failed("misleading 'category is optional' docstring still in agent/tools.py")
    else:
        runner.passed("misleading search_kb docstring corrected in agent/tools.py")


def check_found_feature_pattern(runner: TestRunner):
    """fixes.md surfaces the recurring PDF-export feature request."""
    fixes = runner.read(runner.artifacts[0]).lower()
    if "pdf" in fixes and ("export" in fixes or "download" in fixes):
        cited = [t for t in PDF_REQUEST_TOKENS if t in fixes]
        runner.passed(f"found PDF-export feature-request pattern (tokens cited: {cited})")
    else:
        runner.failed("fixes.md does not surface the PDF-export feature-request pattern")


def check_no_false_positives(runner: TestRunner):
    """Informational LLM judge: does fixes.md invent problems not in the sessions?"""
    fixes = runner.read(runner.artifacts[0])
    prompt = f"""The following fix list was produced by auditing a support agent's
production sessions. The ONLY real issues present in those sessions were:
1. The agent claimed success after a failed update_subscription tool call (2 sessions).
2. The agent called a nonexistent lookup_order_status tool (2 sessions).
3. search_kb tool calls erroring with "category is required" (3 sessions).
4. Users repeatedly requesting PDF export of the conversation (3 sessions).
The remaining 4 sessions were healthy.

Does the fix list stick to these real issues, without inventing problems that
were not present in the sessions? Minor framing differences are fine; fail only
if it asserts a substantial problem pattern that does not correspond to any of
the four real issues above.

Fix list:
{fixes}
"""
    result = evaluate_with_schema(prompt)
    # Informational only — never a hard failure (LLM judges are noisy)
    if result.get("pass"):
        runner.passed("LLM judge: no invented problems")
    else:
        runner.passed(
            f"[info] LLM judge flagged possible invented problems: {result.get('reason')}"
        )


if __name__ == "__main__":
    TestRunner.run(
        [
            check_found_success_after_failure,
            check_found_hallucinated_tool,
            check_found_tool_desc_bug,
            check_found_feature_pattern,
            check_no_false_positives,
        ]
    )
