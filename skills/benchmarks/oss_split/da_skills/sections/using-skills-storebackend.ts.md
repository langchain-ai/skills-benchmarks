Load skills from URL into store:

```typescript
import { createDeepAgent, StoreBackend, type FileData } from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

function createFileData(content: string): FileData {
  const now = new Date().toISOString();
  return {
    content: content.split("\n"),
    created_at: now,
    modified_at: now,
  };
}

const skillUrl = "https://raw.githubusercontent.com/.../SKILL.md";
const response = await fetch(skillUrl);
const skillContent = await response.text();

await store.put(
  ["filesystem"],
  "/skills/langgraph-docs/SKILL.md",
  createFileData(skillContent)
);

const agent = await createDeepAgent({
  backend: (config) => new StoreBackend(config),
  store,
  skills: ["/skills/"]
});
```
