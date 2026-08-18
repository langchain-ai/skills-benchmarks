Send audio content for transcription.

```typescript
// Example with hypothetical audio support
const message = new HumanMessage({
  contentBlocks: [
    { type: "text", text: "Transcribe this audio" },
    {
      type: "audio",
      data: base64Audio,
      mimeType: "audio/mpeg",
    },
  ],
});
```
