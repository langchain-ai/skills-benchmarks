Use FilesystemBackend for local skills:

```typescript
// Skills won't load without proper backend
const agent = await createDeepAgent({
  skills: ["/path/to/skills/"]
});

// Use FilesystemBackend for local skills
import { FilesystemBackend } from "deepagents";

const agent = await createDeepAgent({
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  skills: ["./skills/"]
});
```
