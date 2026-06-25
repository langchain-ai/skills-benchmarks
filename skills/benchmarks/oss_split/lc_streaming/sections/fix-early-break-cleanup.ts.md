Clean up streams on early break:

```typescript
// Problem: Not properly cleaning up
for await (const chunk of await agent.stream(input)) {
  if (someCondition) {
    break;  // Stream may not clean up properly
  }
}

// Solution: Use try/finally or explicit cleanup
const stream = await agent.stream(input);
try {
  for await (const chunk of stream) {
    if (someCondition) {
      break;
    }
  }
} finally {
  // Cleanup if needed
}
```
