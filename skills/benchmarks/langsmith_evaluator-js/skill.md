---
name: langsmith-evaluator-js
description: Use this skill for ANY question about CREATING evaluators (TypeScript/JavaScript CLI). Covers creating custom metrics, LLM as Judge evaluators, code-based evaluators, and uploading evaluation logic to LangSmith. Note that evaluator functions themselves must be Python.
---

<oneliner>
Create evaluators to measure agent performance on your datasets. LangSmith supports two types: **LLM as Judge** (uses LLM to grade outputs) and **Custom Code** (deterministic logic).
</oneliner>

<setup>
Environment Variables

```bash
LANGSMITH_API_KEY=lsv2_pt_your_api_key_here          # Required
LANGSMITH_WORKSPACE_ID=your-workspace-id              # Optional: for org-scoped keys
OPENAI_API_KEY=your_openai_key                        # For LLM as Judge
```

Dependencies (from project root)

```bash
npm install langsmith commander chalk cli-table3 dotenv
```
</setup>

<evaluator_format>
**Note:** LangSmith evaluators must be written in Python, even when using this TypeScript CLI to upload them.

Evaluators use `(run, example)` signature for LangSmith:

```python
def evaluator_name(run, example):
    """Evaluate using run/example dicts.

    Args:
        run: Dict with run["outputs"] containing agent outputs
        example: Dict with example["outputs"] containing expected outputs
    """
    agent_response = run["outputs"].get("expected_response", "")
    expected = example["outputs"].get("expected_response", "")

    return {
        "metric_name": 0.85,      # Metric name as key directly
        "comment": "Reason..."    # Optional explanation
    }
```
</evaluator_format>

<evaluator_types>
- **LLM as Judge** - Uses an LLM to grade outputs. Best for subjective quality (accuracy, helpfulness, relevance). Use structured output for reliable grading.
- **Custom Code** - Deterministic logic. Best for objective checks (exact match, trajectory validation, format compliance).
- **Trajectory Evaluators** - Check tool call sequences. Compare `run["outputs"]["expected_trajectory"]` against expected.
</evaluator_types>

<code_evaluators>
### Exact Match

```python
def exact_match_evaluator(run, example):
    output = run["outputs"].get("expected_response", "").strip().lower()
    expected = example["outputs"].get("expected_response", "").strip().lower()
    match = output == expected
    return {"exact_match": 1 if match else 0, "comment": f"Match: {match}"}
```

### Trajectory Validation

```python
def trajectory_evaluator(run, example):
    trajectory = run["outputs"].get("expected_trajectory", [])
    expected = example["outputs"].get("expected_trajectory", [])
    exact = trajectory == expected
    all_tools = set(expected).issubset(set(trajectory))
    return {
        "trajectory_match": 1 if exact else 0,
        "comment": f"Exact: {exact}, All tools: {all_tools}"
    }
```
</code_evaluators>

<upload>
Use the included script to upload evaluators.

```bash
# List existing evaluators
npx tsx upload_evaluators.ts list

# Upload evaluator
npx tsx upload_evaluators.ts upload my_evaluators.py \
  --name "Trajectory Match" \
  --function trajectory_match \
  --dataset "Skills: Trajectory" \
  --replace

# Delete evaluator
npx tsx upload_evaluators.ts delete "Trajectory Match"
```

**IMPORTANT - Safety Prompts:**
- The script prompts for confirmation before destructive operations
- **NEVER use `--yes` flag unless the user explicitly requests it**
</upload>

<best_practices>
1. **Use structured output for LLM judges** - More reliable than parsing free-text
2. **Match evaluator to dataset type**
   - Final Response → LLM as Judge for quality
   - Trajectory → Custom Code for sequence
3. **Use async for LLM judges** - Enables parallel evaluation
4. **Test evaluators independently** - Validate on known good/bad examples first
</best_practices>

<example_workflow>
Complete workflow to create and upload an evaluator:

```bash
# 1. Create evaluators file
cat > evaluators.py <<'EOF'
def exact_match(run, example):
    """Check if output exactly matches expected."""
    output = run["outputs"].get("expected_response", "").strip().lower()
    expected = example["outputs"].get("expected_response", "").strip().lower()
    match = output == expected
    return {"exact_match": 1 if match else 0, "comment": f"Match: {match}"}
EOF

# 2. Upload to LangSmith
npx tsx upload_evaluators.ts upload evaluators.py \
  --name "Exact Match" \
  --function exact_match \
  --dataset "Skills: Final Response" \
  --replace

# 3. Evaluator runs automatically on new dataset runs
```
</example_workflow>

<related_skills>
- **langsmith-trace-js**: Queries execution data. Traces show what tools were called, helping you understand what evaluators should check.
- **langsmith-dataset-js**: Generates evaluation datasets. Evaluators validate the expected outputs defined in datasets.
</related_skills>
