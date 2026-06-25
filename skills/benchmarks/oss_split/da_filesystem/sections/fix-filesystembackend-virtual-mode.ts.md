Enable virtualMode to restrict paths:

```typescript
// Insecure
new FilesystemBackend({ rootDir: "/project", virtualMode: false })

// Secure
new FilesystemBackend({ rootDir: "/project", virtualMode: true })
```
