Access result messages correctly:

```typescript
const result = await agent.invoke({ messages: [{ role: "user", content: "Hello" }] });
console.log(result.messages);  // Array of all messages - correct
// console.log(result.content); // undefined! - wrong
```
