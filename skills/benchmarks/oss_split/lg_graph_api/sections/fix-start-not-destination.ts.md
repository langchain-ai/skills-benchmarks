Use named entry node instead:

```typescript
// WRONG - Cannot route back to START
builder.addEdge("nodeA", START);  // Error!

// CORRECT - Use named entry node instead
builder.addNode("entry", entryFunc);
builder.addEdge(START, "entry");
builder.addEdge("nodeA", "entry");  // OK
```
