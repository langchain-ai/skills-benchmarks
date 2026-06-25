Provide backend for skill loading:

```typescript
// No backend
await createDeepAgent({ skills: ["./skills/"] });

// Provide backend
await createDeepAgent({
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  skills: ["./skills/"]
});
```
