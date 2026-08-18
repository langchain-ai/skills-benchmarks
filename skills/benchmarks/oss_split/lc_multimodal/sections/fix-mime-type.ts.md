Always include mimeType with base64 data.

```typescript
// Problem: No MIME type
{ type: "image", data: base64Data }  // May fail

// Solution: Always include MIME type
{ type: "image", data: base64Data, mimeType: "image/jpeg" }
```
