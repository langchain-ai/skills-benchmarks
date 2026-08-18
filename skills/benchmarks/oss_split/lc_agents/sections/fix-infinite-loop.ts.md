Limit iterations to prevent runaway agents:

```typescript
const result = await agent.invoke(
  { messages: [["user", "Do research"]] },
  { recursionLimit: 10 },
);
```
