TypeScript equivalent with Zod schema:

```typescript
import { tool } from "langchain";
import { z } from "zod";

const calculator = tool(
  async ({ operation, a, b }: { operation: string; a: number; b: number }) => {
    if (operation === "add") return a + b;
    if (operation === "subtract") return a - b;
    if (operation === "multiply") return a * b;
    if (operation === "divide") return a / b;
    throw new Error(`Unknown operation: ${operation}`);
  },
  {
    name: "calculator",
    description: "Perform mathematical calculations. Use this when you need to compute numbers.",
    schema: z.object({
      operation: z.enum(["add", "subtract", "multiply", "divide"]).describe("The mathematical operation"),
      a: z.number().describe("First number"),
      b: z.number().describe("Second number"),
    }),
  }
);

const result = await calculator.invoke({ operation: "add", a: 5, b: 3 });
console.log(result); // "8"
```
