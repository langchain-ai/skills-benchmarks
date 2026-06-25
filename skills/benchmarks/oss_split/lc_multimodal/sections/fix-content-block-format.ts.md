Use standard contentBlocks instead of old format.

```typescript
// Problem: Old format
const message = new HumanMessage({
  content: [
    { type: "image_url", image_url: { url: "..." } }  // OpenAI-specific
  ]
});

// Solution: Use standard content blocks
const message = new HumanMessage({
  contentBlocks: [
    { type: "image", url: "..." }  // Cross-provider
  ]
});
```
