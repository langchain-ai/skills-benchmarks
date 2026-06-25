Iterate over stream correctly:

```typescript
// Problem: Not awaiting stream
const stream = model.stream("Hello");
console.log(stream); // Promise, not chunks

// Solution: Use for await
const stream = await model.stream("Hello");
for await (const chunk of stream) {
  console.log(chunk.content);
}
```
