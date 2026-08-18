Iterate over stream or use invoke.

```typescript
// Mixing streaming and non-streaming incorrectly
const response = await model.stream("Hello");
console.log(response.content); // Won't work! response is an async iterable

// Handle streaming properly
const stream = await model.stream("Hello");
for await (const chunk of stream) {
  console.log(chunk.content);
}

// OR use invoke for non-streaming
const response = await model.invoke("Hello");
console.log(response.content);
```
