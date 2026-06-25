Offload search results to filesystem:

```typescript
const agent = await createDeepAgent({});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Search for TypeScript best practices and save results for analysis"
  }]
});
// Agent: search -> write_file -> compact context -> read_file when needed
```
