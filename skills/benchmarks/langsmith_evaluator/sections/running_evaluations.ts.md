```javascript
import { Client } from "langsmith";

const client = new Client();

async function runAgent(inputs) {
  const result = await yourAgent.invoke(inputs);
  return { response: result };
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
