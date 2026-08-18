Write clear, specific tool descriptions.

```typescript
// Poor description
const myTool = tool(
  async ({ x }) => x * 2,
  {
    name: "tool1",
    description: "A tool", // Too vague!
    schema: z.object({ x: z.number() }),
  }
);

// Clear, specific description
const myTool = tool(
  async ({ number }) => number * 2,
  {
    name: "double_number",
    description: "Multiply a number by 2. Use this when the user wants to double a value.",
    schema: z.object({
      number: z.number().describe("The number to double"),
    }),
  }
);
```
