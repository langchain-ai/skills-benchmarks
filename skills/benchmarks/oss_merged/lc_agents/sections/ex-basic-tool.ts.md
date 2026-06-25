Define a calculator tool using the tool() function with Zod schema validation.
```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const calculator = tool(
  async ({ operation, a, b }) => {
    const ops = { add: a + b, subtract: a - b, multiply: a * b, divide: a / b };
    return ops[operation];
  },
  {
    name: "calculator",
    description: "Perform mathematical calculations.",
    schema: z.object({
      operation: z.enum(["add", "subtract", "multiply", "divide"]),
      a: z.number().describe("First number"),
      b: z.number().describe("Second number"),
    }),
  }
);
```
