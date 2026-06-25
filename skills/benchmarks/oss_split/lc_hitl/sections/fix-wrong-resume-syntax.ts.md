Use `Command(resume={...})` (Python) or `new Command({ resume: {...} })` (TypeScript), not a plain dict/object.

Use Command class to resume.

```typescript
// Problem: Wrong resume format
await agent.invoke({
  resume: { decisions: [...] }  // Wrong!
});

// Solution: Use Command
import { Command } from "@langchain/langgraph";

await agent.invoke(
  new Command({
    resume: { decisions: [{ type: "approve" }] }
  }),
  config
);
```
