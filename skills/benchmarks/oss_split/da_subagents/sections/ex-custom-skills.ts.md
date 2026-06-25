Provide skills explicitly to subagent:

```typescript
const agent = await createDeepAgent({
  skills: ["/main-skills/"],
  subagents: [
    {
      name: "python-expert",
      description: "Python code review and refactoring",
      systemPrompt: "Review Python code for best practices",
      tools: [readCode, suggestImprovements],
      skills: ["/python-skills/"],  // Subagent-specific
    }
  ]
});
// Custom subagents DON'T inherit main skills by default
// General-purpose subagent DOES inherit main skills
```
