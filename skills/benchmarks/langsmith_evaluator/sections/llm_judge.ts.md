Use OpenAI with JSON mode for reliable grading:

```javascript
import OpenAI from "openai";

const openai = new OpenAI();

async function accuracyEvaluator(run, example) {
  const expected = example.outputs?.response ?? "";
  const agentOutput = run.outputs?.response ?? "";

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
