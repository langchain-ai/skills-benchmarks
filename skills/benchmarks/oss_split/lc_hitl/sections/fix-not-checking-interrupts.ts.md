Check for `"__interrupt__"` in the result before assuming the agent completed.

Check for interrupt before processing result.

```typescript
// Problem: Not detecting interrupt
const result = await agent.invoke(input, config);
console.log(result.messages);  // May not have completed!

// Solution: Check for __interrupt__
if ("__interrupt__" in result) {
  // Handle human decision
} else {
  // Agent completed
}
```
