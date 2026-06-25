Use PostgresStore for production (InMemoryStore lost on restart).
```typescript
// WRONG                                    // CORRECT
const store = new InMemoryStore();          const store = new PostgresStore({ connectionString: "..." });
```
