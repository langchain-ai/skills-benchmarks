Define a calculator tool using the tool() function with Zod schema validation.
```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const calculate = tool(
  async ({ expression }) => {
    const allowed = new Set("0123456789+-*/(). ".split(""));
    if (![...expression].every((c) => allowed.has(c))) {
      return "Error: Invalid characters in expression";
    }
    try {
      return String(eval(expression));
    } catch (e) {
      return `Error: ${e}`;
    }
  },
  {
    name: "calculate",
    description: "Evaluate a mathematical expression safely.",
    schema: z.object({
      expression: z.string().describe("Math expression like '2 + 2' or '10 * 5'"),
    }),
  }
);
```
