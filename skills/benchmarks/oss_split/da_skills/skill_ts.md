---
name: Deep Agents Skills (TypeScript)
description: [Deep Agents] Creating and using custom skills with progressive disclosure, SKILL.md format, and the Agent Skills protocol in Deep Agents.
---

# deepagents-skills (JavaScript/TypeScript)

## Overview

Skills provide specialized capabilities through **progressive disclosure**: agents load content only when relevant.

**Process:** Match (see descriptions) → Read (load SKILL.md) → Execute (follow instructions)

## Skills vs Memory

| Skills | Memory (AGENTS.md) |
|--------|-------------------|
| On-demand loading | Always loaded |
| Task-specific | General preferences |
| Large docs | Compact context |

## Using Skills

### With FilesystemBackend

```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  skills: ["./skills/"],
  checkpointer: new MemorySaver()
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "What is LangGraph? Use langgraph-docs skill if available."
  }]
});
```

### With StoreBackend

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

### With StateBackend

```typescript
import { createDeepAgent, type FileData } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

function createFileData(content: string): FileData {
  const now = new Date().toISOString();
  return { content: content.split("\n"), created_at: now, modified_at: now };
}

const skillContent = `---
name: python-testing
description: Pytest best practices
---
# Python Testing Skill
...`;

const skillsFiles: Record<string, FileData> = {
  "/skills/python-testing/SKILL.md": createFileData(skillContent)
};

const agent = await createDeepAgent({
  skills: ["/skills/"],
  checkpointer: new MemorySaver()
});

await agent.invoke({
  messages: [{ role: "user", content: "How should I write tests?" }],
  files: skillsFiles
});
```

## SKILL.md Format

```markdown

# FastAPI Documentation Skill

## When to Use
When working with FastAPI endpoints.

## Instructions
Always use async handlers:
\`\`\`typescript
app.get("/users/:id", async (req, res) => {
  const user = await db.users.findById(req.params.id);
  res.json(user);
});
\`\`\`
```

## Gotchas

### 1. Skills Need Backend

```typescript
// ❌ No backend
await createDeepAgent({ skills: ["./skills/"] });

// ✅ Provide backend
await createDeepAgent({
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  skills: ["./skills/"]
});
```

### 2. Frontmatter Required

```markdown
# ❌ Missing
# My Skill

# ✅ Include
# My Skill
```

### 3. Specific Descriptions

```markdown
# ❌ Vague
description: Helpful skill

# ✅ Specific
description: TypeScript testing with Jest and mocking patterns
```

## Full Documentation

- [Skills Guide](https://docs.langchain.com/oss/javascript/deepagents/skills)
- [Agent Skills Protocol](https://docs.langchain.com/oss/javascript/langchain/multi-agent/skills)
