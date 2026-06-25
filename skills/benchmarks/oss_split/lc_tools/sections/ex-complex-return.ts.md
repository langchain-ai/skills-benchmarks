TypeScript equivalent:

```typescript
const analyzeText = tool(
  async ({ text }) => {
    const words = text.split(/\s+/);
    return JSON.stringify({
      word_count: words.length,
      char_count: text.length,
      sentences: text.split(/[.!?]+/).length,
      avg_word_length: words.reduce((sum, w) => sum + w.length, 0) / words.length,
    });
  },
  {
    name: "analyze_text",
    description: "Analyze text statistics",
    schema: z.object({
      text: z.string().describe("Text to analyze"),
    }),
  }
);
```
