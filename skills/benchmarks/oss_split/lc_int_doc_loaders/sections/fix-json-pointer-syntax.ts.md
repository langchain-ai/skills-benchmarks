JSONPointer starts with /:

```typescript
// Wrong JSON pointer format
const loader = new JSONLoader("data.json", ["texts.content"]);

// Correct JSON pointer format (starts with /)
const loader = new JSONLoader("data.json", ["/texts/0/content"]);
```
