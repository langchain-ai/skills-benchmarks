TypeScript equivalent:

```typescript
const divisionTool = tool(
  async ({ numerator, denominator }) => {
    if (denominator === 0) {
      throw new Error("Cannot divide by zero");
    }
    return numerator / denominator;
  },
  {
    name: "divide",
    description: "Divide two numbers",
    schema: z.object({
      numerator: z.number(),
      denominator: z.number(),
    }),
  }
);
```
