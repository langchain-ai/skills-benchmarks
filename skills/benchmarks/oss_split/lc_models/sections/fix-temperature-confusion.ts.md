Use correct temperature range:

```typescript
// Problem: Wrong temperature range
const model = new ChatOpenAI({
  temperature: 10, // Too high! Should be 0-1
});

// Solution: Use 0-1 range
const deterministic = new ChatOpenAI({ temperature: 0 }); // Always same
const balanced = new ChatOpenAI({ temperature: 0.7 }); // Default
const creative = new ChatOpenAI({ temperature: 1 }); // Maximum randomness
```
