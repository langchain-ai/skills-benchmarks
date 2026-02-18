---
name: Deep Agents Skills
description: [Deep Agents] Creating and using custom skills with progressive disclosure, SKILL.md format, and the Agent Skills protocol in Deep Agents.
---

## Overview

Skills are reusable agent capabilities that provide specialized workflows and domain knowledge. They use **progressive disclosure**: agents only load skill content when it's relevant to the task.

**How it works:**
1. **Match**: Agent sees skill descriptions in system prompt
2. **Read**: If relevant, agent reads full SKILL.md using read_file
3. **Execute**: Agent follows instructions and accesses supporting files

## Skills vs Memory

| Skills | Memory (AGENTS.md) |
|--------|-------------------|
| On-demand loading | Always loaded at startup |
| Task-specific instructions | General preferences |
| Large documentation | Compact context |
| SKILL.md in directories | Single AGENTS.md file |

## Creating Skills

### Skill Directory Structure

```
skills/
└── langgraph-docs/
    ├── SKILL.md        # Required: main skill file
    ├── examples.py     # Optional: supporting files
    └── templates/      # Optional: templates
```

### SKILL.md Format

```markdown

# LangGraph Documentation Skill

## Overview
This skill provides access to LangGraph documentation for answering questions.

## When to Use
Use this skill when the user asks about LangGraph features, APIs, or usage.

## Instructions
1. Search documentation for relevant topics
2. Provide code examples from examples.py
3. Link to official docs

## Supporting Files
- examples.py: Common usage patterns
- templates/graph.py: Graph template
```

## Using Skills in Agents

### With FilesystemBackend

#### Python

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"],  # Path to skills directory
    checkpointer=MemorySaver()
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "What is LangGraph? Use the langgraph-docs skill if available."
    }]
})
```

#### TypeScript

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

#### Python

```python
from urllib.request import urlopen
from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Load skill from URL
skill_url = "https://raw.githubusercontent.com/langchain-ai/deepagents/main/libs/cli/examples/skills/langgraph-docs/SKILL.md"
with urlopen(skill_url) as response:
    skill_content = response.read().decode('utf-8')

# Put skill in store
store.put(
    namespace=("filesystem",),
    key="/skills/langgraph-docs/SKILL.md",
    value=create_file_data(skill_content)
)

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=store,
    skills=["/skills/"]
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "What is LangGraph?"
    }]
})
```

#### TypeScript

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

### With StateBackend (In-State Files)

#### Python

```python
from deepagents import create_deep_agent
from deepagents.backends.utils import create_file_data
from langgraph.checkpoint.memory import MemorySaver

# Prepare skill content
skill_content = """---
name: python-testing
description: Best practices for Python testing with pytest
---
# Python Testing Skill
..."""

skills_files = {
    "/skills/python-testing/SKILL.md": create_file_data(skill_content)
}

agent = create_deep_agent(
    skills=["/skills/"],
    checkpointer=MemorySaver()
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "How should I write tests?"
    }],
    "files": skills_files  # Seed state with skill files
})
```

#### TypeScript

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

## Decision Table: When to Create Skills

| Create a Skill When | Use Memory Instead |
|--------------------|--------------------|
| Instructions are task-specific | Context always relevant |
| Content is large (>500 lines) | Content is compact |
| Only needed occasionally | Needed every session |
| Multiple supporting files | Single preference |
| Domain-specific expertise | General preferences |

## Example Skills

### Example 1: API Documentation Skill

```markdown

# FastAPI Documentation Skill

## Endpoints
Always use async handlers:
\`\`\`python
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
\`\`\`

## Validation
Use Pydantic models for request/response validation.

## Supporting Files
See endpoints.py for complete examples.
```

### Example 2: Testing Skill (Python)

```markdown

# Pytest Patterns Skill

## Fixtures
\`\`\`python
@pytest.fixture
async def db_session():
    async with AsyncSession(engine) as session:
        yield session
        await session.rollback()
\`\`\`

## Mocking
Use pytest-mock for external dependencies.
```

### Example 3: Testing Skill (TypeScript)

```markdown

# Jest Testing Skill

## When to Use
When writing unit or integration tests in TypeScript/JavaScript.

## Instructions
Always use async handlers:
\`\`\`typescript
app.get("/users/:id", async (req, res) => {
  const user = await db.users.findById(req.params.id);
  res.json(user);
});
\`\`\`
```

## Boundaries

### What Agents CAN Do
- Load skills on-demand when relevant
- Read SKILL.md and supporting files
- Follow skill instructions
- Update skills (if permitted)
- Create new skills

### What Agents CANNOT Do
- Load all skills at startup (only descriptions)
- Change the SKILL.md frontmatter format
- Access skills outside configured directories
- Share skills across agents without proper backend

## Gotchas

### 1. Skills Require Backend Setup

#### Python

```python
# Skills won't load without backend
agent = create_deep_agent(
    skills=["./skills/"]
)

# Provide backend
agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"]
)
```

#### TypeScript

```typescript
// No backend
await createDeepAgent({ skills: ["./skills/"] });

// Provide backend
await createDeepAgent({
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  skills: ["./skills/"]
});
```

### 2. Frontmatter is Required

```markdown
# Missing frontmatter - WON'T WORK
# My Skill
This is my skill...

# Include frontmatter - CORRECT
# My Skill
```

### 3. Skill Descriptions Drive Discovery

```markdown
# Vague description - BAD
description: Helpful skill

# Specific description - GOOD
description: Python testing best practices with pytest fixtures and mocking
```

### 4. Custom Subagents Don't Inherit Skills

#### Python

```python
# Main agent skills NOT inherited by custom subagents
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{"name": "helper", ...}]  # No skills
)

# Provide skills to subagent explicitly
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{
        "name": "helper",
        "skills": ["/helper-skills/"],  # Explicit
        ...
    }]
)
```

#### TypeScript

```typescript
// No inherited skills
await createDeepAgent({
  skills: ["/main-skills/"],
  subagents: [{ name: "helper", ... }]
});

// Provide skills explicitly
await createDeepAgent({
  skills: ["/main-skills/"],
  subagents: [{
    name: "helper",
    skills: ["/helper-skills/"],
    ...
  }]
});
```

## Links to Documentation

### Python
- [Skills Guide](https://docs.langchain.com/oss/python/deepagents/skills)
- [Agent Skills Protocol](https://docs.langchain.com/oss/python/langchain/multi-agent/skills)
- [Progressive Disclosure](https://docs.langchain.com/oss/python/langchain/multi-agent/skills-sql-assistant)

### TypeScript
- [Skills Guide](https://docs.langchain.com/oss/javascript/deepagents/skills)
- [Agent Skills Protocol](https://docs.langchain.com/oss/javascript/langchain/multi-agent/skills)
