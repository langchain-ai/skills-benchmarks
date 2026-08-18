Use conditional edges with END return to break loops.
```typescript
// WRONG: Loops forever
builder.addEdge("node_a", "node_b").addEdge("node_b", "node_a");

// CORRECT
builder.addConditionalEdges("node_a", (state) => state.count > 10 ? END : "node_b");
```
