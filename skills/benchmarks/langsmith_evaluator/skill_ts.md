---
name: langsmith-evaluator-js
description: Use this skill for questions about CREATING evaluators. Covers creating custom metrics, LLM as Judge evaluators, code-based evaluators, and uploading evaluation logic to LangSmith.
---

<oneliner>
Create JavaScript evaluators to measure agent performance on your datasets. LangSmith supports two types: **LLM as Judge** (uses LLM to grade outputs) and **Custom Code** (deterministic logic).
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
npm install langsmith commander chalk cli-table3 dotenv openai
```
</setup>

<evaluator_format>
JavaScript evaluators use `(run, example)` signature for offline (dataset) evaluations:

```javascript
function evaluatorName(run, example) {
  // run contains the agent's actual outputs
  // example contains the expected outputs from the dataset
  const agentResponse = run.outputs?.expected_response ?? "";
  const expected = example.outputs?.expected_response ?? "";

  const score = agentResponse === expected ? 1 : 0;
  return { metric_name: score, comment: "Reason..." };
}
```

For online evaluators (no dataset), only `run` is available:

```javascript
function onlineEvaluator(run) {
  const output = run.outputs?.response ?? "";
  const score = output.length > 0 ? 1 : 0;
  return { has_response: score };
}
```
</evaluator_format>

<evaluator_types>
- **LLM as Judge** - Uses an LLM to grade outputs. Best for subjective quality (accuracy, helpfulness, relevance).
- **Custom Code** - Deterministic logic. Best for objective checks (exact match, trajectory validation, format compliance).
- **Trajectory Evaluators** - Check tool call sequences. Compare `run.outputs.expected_trajectory` against expected.
</evaluator_types>

<llm_judge>
Use OpenAI with JSON mode for reliable grading:

```javascript
import OpenAI from "openai";

const openai = new OpenAI();

async function accuracyEvaluator(run, example) {
  const expected = example.outputs?.expected_response ?? "";
  const agentOutput = run.outputs?.expected_response ?? "";

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    temperature: 0,
    response_format: { type: "json_object" },
    messages: [
      {
        role: "system",
        content: `You are an evaluator. Respond with JSON: {"is_accurate": boolean, "reasoning": string, "confidence": number}`
      },
      {
        role: "user",
        content: `Expected: ${expected}\nAgent Output: ${agentOutput}\n\nIs the agent output accurate?`
      }
    ]
  });

  const grade = JSON.parse(response.choices[0].message.content);
  return {
    accuracy: grade.is_accurate ? 1 : 0,
    comment: `${grade.reasoning} (confidence: ${grade.confidence})`
  };
}
```
</llm_judge>

<code_evaluators>
### Exact Match

```javascript
function exactMatchEvaluator(run, example) {
  const output = (run.outputs?.expected_response ?? "").trim().toLowerCase();
  const expected = (example.outputs?.expected_response ?? "").trim().toLowerCase();
  const match = output === expected;
  return { exact_match: match ? 1 : 0, comment: `Match: ${match}` };
}
```

### Trajectory Validation

```javascript
function trajectoryEvaluator(run, example) {
  const trajectory = run.outputs?.expected_trajectory ?? [];
  const expected = example.outputs?.expected_trajectory ?? [];
  const exact = JSON.stringify(trajectory) === JSON.stringify(expected);
  const allTools = expected.every(tool => trajectory.includes(tool));
  return {
    trajectory_match: exact ? 1 : 0,
    comment: `Exact: ${exact}, All tools: ${allTools}`
  };
}
```

### Contains Keywords

```javascript
function containsKeywords(run, example) {
  const output = (run.outputs?.response ?? "").toLowerCase();
  const keywords = example.outputs?.required_keywords ?? [];
  const found = keywords.filter(kw => output.includes(kw.toLowerCase()));
  const score = found.length / keywords.length;
  return {
    keyword_coverage: score,
    comment: `Found ${found.length}/${keywords.length} keywords`
  };
}
```
</code_evaluators>

<upload>
Use the included script to upload JavaScript evaluators.

```bash
# List existing evaluators
npx tsx upload_evaluators.ts list

# Upload JavaScript evaluator
npx tsx upload_evaluators.ts upload my_evaluators.js \
  --name "Exact Match" \
  --function exactMatchEvaluator \
  --dataset "Skills: Final Response" \
  --replace

# Upload from TypeScript file
npx tsx upload_evaluators.ts upload my_evaluators.ts \
  --name "Trajectory Match" \
  --function trajectoryEvaluator \
  --dataset "Skills: Trajectory" \
  --replace

# Delete evaluator
npx tsx upload_evaluators.ts delete "Exact Match"
```

**IMPORTANT - Safety Prompts:**
- The script prompts for confirmation before destructive operations
- **NEVER use `--yes` flag unless the user explicitly requests it**
</upload>

<best_practices>
1. **Use JSON mode for LLM judges** - More reliable than parsing free-text
2. **Match evaluator to dataset type**
   - Final Response → LLM as Judge for quality
   - Trajectory → Custom Code for sequence
3. **Handle missing fields gracefully** - Use `??` or optional chaining
4. **Test evaluators locally first** - Validate on known good/bad examples before uploading
</best_practices>

<example_workflow>
Complete workflow to create and upload a JavaScript evaluator:

```bash
# 1. Create evaluators file
cat > evaluators.js <<'EOF'
function exactMatch(run, example) {
  // Check if output exactly matches expected
  const output = (run.outputs?.expected_response ?? "").trim().toLowerCase();
  const expected = (example.outputs?.expected_response ?? "").trim().toLowerCase();
  const match = output === expected;
  return { exact_match: match ? 1 : 0, comment: `Match: ${match}` };
}
EOF

# 2. Upload to LangSmith
npx tsx upload_evaluators.ts upload evaluators.js \
  --name "Exact Match" \
  --function exactMatch \
  --dataset "Skills: Final Response" \
  --replace

# 3. Evaluator runs automatically on new dataset runs
```
</example_workflow>

<running_evaluations>
```javascript
import { Client } from "langsmith";

const client = new Client();

async function runAgent(inputs) {
  const result = await yourAgent.invoke(inputs);
  return { expected_response: result };
}

const results = await client.evaluate(
  runAgent,
  {
    data: "Skills: Final Response",
    evaluators: [exactMatchEvaluator, accuracyEvaluator],
    experimentPrefix: "skills-eval-v1",
    maxConcurrency: 4
  }
);
```
</running_evaluations>

<resources>
- [LangSmith Evaluation Concepts](https://docs.langchain.com/langsmith/evaluation-concepts)
- [Custom Code Evaluators](https://changelog.langchain.com/announcements/custom-code-evaluators-in-langsmith)
- [OpenEvals - Readymade Evaluators](https://github.com/langchain-ai/openevals)
</resources>

