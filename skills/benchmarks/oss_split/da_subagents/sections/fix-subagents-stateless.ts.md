Each call creates fresh subagent:

```typescript
// Subagents don't remember previous calls
await agent.invoke({messages: [{role: "user", content: "Research X"}]});
await agent.invoke({messages: [{role: "user", content: "What did you find?"}]});
// Fresh subagent each time

// Main agent maintains conversation memory
```
