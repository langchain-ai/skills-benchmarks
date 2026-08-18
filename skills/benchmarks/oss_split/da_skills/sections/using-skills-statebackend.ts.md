Seed state with skill files:

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
