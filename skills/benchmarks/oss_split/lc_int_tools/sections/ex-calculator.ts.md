Evaluate math expressions with calculator tool.

```typescript
import { Calculator } from "@langchain/community/tools/calculator";

const calculator = new Calculator();

// Perform calculations
const result = await calculator.invoke("sqrt(144) + 5 * 3");
console.log(result); // "27"

// Use in agent for math problems
const mathAgent = createAgent({
  model: "gpt-4.1",
  tools: [calculator],
});
```
