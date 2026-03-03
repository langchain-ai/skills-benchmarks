---
name: deep-agents-skills-py
description: "[Deep Agents] Creating and using custom skills with progressive disclosure, SKILL.md format, and the Agent Skills protocol in Deep Agents."
---

<overview>
Skills are reusable agent capabilities that provide specialized workflows and domain knowledge. They use **progressive disclosure**: agents only load skill content when it's relevant to the task.

**How it works:**
1. **Match**: Agent sees skill descriptions in system prompt
2. **Read**: If relevant, agent reads full SKILL.md using read_file
3. **Execute**: Agent follows instructions and accesses supporting files
</overview>

<skills-vs-memory>

| Skills | Memory (AGENTS.md) |
|--------|-------------------|
| On-demand loading | Always loaded at startup |
| Task-specific instructions | General preferences |
| Large documentation | Compact context |
| SKILL.md in directories | Single AGENTS.md file |

</skills-vs-memory>

<skill-directory-structure>
```
skills/
└── langgraph-docs/
    ├── SKILL.md        # Required: main skill file
    ├── examples.py     # Optional: supporting files
    └── templates/      # Optional: templates
```
</skill-directory-structure>

<skill-md-format>
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
</skill-md-format>

<ex-filesystem-backend>
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
</ex-filesystem-backend>

<ex-store-backend>
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
</ex-store-backend>

<ex-state-backend>
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
</ex-state-backend>

<when-to-create-skills>

| Create a Skill When | Use Memory Instead |
|--------------------|--------------------|
| Instructions are task-specific | Context always relevant |
| Content is large (>500 lines) | Content is compact |
| Only needed occasionally | Needed every session |
| Multiple supporting files | Single preference |
| Domain-specific expertise | General preferences |

</when-to-create-skills>

<ex-api-documentation-skill>
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
</ex-api-documentation-skill>

<ex-testing-skill>
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
</ex-testing-skill>

<boundaries>
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
</boundaries>

<fix-backend-required>
```python
# WRONG: Skills won't load without backend
agent = create_deep_agent(
    skills=["./skills/"]
)

# CORRECT: Provide backend
agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"]
)
```
</fix-backend-required>

<fix-frontmatter-required>
```markdown
# WRONG: Missing frontmatter
# My Skill
This is my skill...

# CORRECT: Include frontmatter
# My Skill
```
</fix-frontmatter-required>

<fix-specific-descriptions>
```markdown
# WRONG: Vague description
description: Helpful skill

# CORRECT: Specific description
description: Python testing best practices with pytest fixtures and mocking
```
</fix-specific-descriptions>

<fix-subagent-skills>
```python
# Main agent skills NOT inherited by custom subagents
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{"name": "helper", ...}]  # No skills
)

# CORRECT: Provide skills to subagent explicitly
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{
        "name": "helper",
        "skills": ["/helper-skills/"],  # Explicit
        ...
    }]
)
```
</fix-subagent-skills>

<links>
- [Skills Guide](https://docs.langchain.com/oss/python/deepagents/skills)
- [Agent Skills Protocol](https://docs.langchain.com/oss/python/langchain/multi-agent/skills)
- [Progressive Disclosure](https://docs.langchain.com/oss/python/langchain/multi-agent/skills-sql-assistant)
</links>
