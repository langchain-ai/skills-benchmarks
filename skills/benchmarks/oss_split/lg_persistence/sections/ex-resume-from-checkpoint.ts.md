Time travel: browse checkpoint history and replay or fork from a past state.
```typescript
const config = { configurable: { thread_id: "session-1" } };

const result = await graph.invoke({ messages: ["start"] }, config);

// Browse checkpoint history (async iterable, collect to array)
const states: Awaited<ReturnType<typeof graph.getState>>[] = [];
for await (const state of graph.getStateHistory(config)) {
  states.push(state);
}

// Replay from a past checkpoint
const past = states[states.length - 2];
const replayed = await graph.invoke(null, past.config);  // null = resume from checkpoint

// Or fork: update state at a past checkpoint, then resume
const forkConfig = await graph.updateState(past.config, { messages: ["edited"] });
const forked = await graph.invoke(null, forkConfig);
```
