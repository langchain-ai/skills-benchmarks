Access response content correctly:

```typescript
// Problem: Wrong property access
const response = await model.invoke("Hello");
console.log(response); // AIMessage object, not string

// Solution: Access .content property
console.log(response.content); // "Hello! How can I help you?"

// Or use .toString()
console.log(response.toString());
```
