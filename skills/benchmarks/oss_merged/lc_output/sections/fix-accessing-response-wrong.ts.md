With withStructuredOutput, response IS the structured data.
```typescript
const response = await structuredModel.invoke("...");
console.log(response);  // Directly the parsed object
```
