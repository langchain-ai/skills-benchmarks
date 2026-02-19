---
name: Deep Agents Skills (TypeScript)
description: "[Deep Agents] Creating and using custom skills with progressive disclosure, SKILL.md format, and the Agent Skills protocol in Deep Agents."
---

<overview>
Skills provide specialized capabilities through **progressive disclosure**: agents load content only when relevant.

**Process:** Match (see descriptions) → Read (load SKILL.md) → Execute (follow instructions)
</overview>

<skills-vs-memory>
| Skills | Memory (AGENTS.md) |
|--------|-------------------|
| On-demand loading | Always loaded |
| Task-specific | General preferences |
| Large docs | Compact context |
</skills-vs-memory>

<ex-with-filesystembackend>
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
</ex-with-filesystembackend>

<ex-with-storebackend>
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
</ex-with-storebackend>

<ex-with-statebackend>
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
</ex-with-statebackend>

<skill-md-format>
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
</skill-md-format>

<fix-skills-need-backend>
```typescript
// WRONG: No backend
await createDeepAgent({ skills: ["./skills/"] });

// CORRECT: Provide backend
await createDeepAgent({
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  skills: ["./skills/"]
});
```
</fix-skills-need-backend>

<fix-frontmatter-required>
```markdown
# WRONG: Missing
# My Skill

# CORRECT: Include
# My Skill
```
</fix-frontmatter-required>

<fix-specific-descriptions>
```markdown
# WRONG: Vague
description: Helpful skill

# CORRECT: Specific
description: TypeScript testing with Jest and mocking patterns
```
</fix-specific-descriptions>

<documentation-links>
- [Skills Guide](https://docs.langchain.com/oss/javascript/deepagents/skills)
- [Agent Skills Protocol](https://docs.langchain.com/oss/javascript/langchain/multi-agent/skills)
</documentation-links>
