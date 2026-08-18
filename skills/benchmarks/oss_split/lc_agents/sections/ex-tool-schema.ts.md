Tool with typed parameters:

```typescript
const calculatorTool = tool(
  async ({ operation, a, b }: { operation: string; a: number; b: number }) => {
    const ops: Record<string, () => number> = {
      add: () => a + b, subtract: () => a - b, multiply: () => a * b, divide: () => a / b,
    };
    return ops[operation]();
  },
  {
    name: "calculate",
    description: "Perform a mathematical calculation",
    schema: z.object({
      operation: z.enum(["add", "subtract", "multiply", "divide"]),
      a: z.number().describe("First number"),
      b: z.number().describe("Second number"),
    }),
  }
);
```
