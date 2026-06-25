Full configuration with all options:

```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";
import { MemorySaver, InMemoryStore } from "@langchain/langgraph";

const agent = await createDeepAgent({
  name: "my-assistant",            // Optional: agent name
  model: "claude-sonnet-4-5-20250929",  // Model to use
  tools: [customTool1, customTool2],    // Additional tools
  systemPrompt: "Custom instructions",   // Custom system prompt
  middleware: [customMiddleware],        // Additional middleware
  subagents: [researchAgent, codeAgent], // Custom subagents
  backend: new FilesystemBackend({ rootDir: "." }),  // Storage backend
  interruptOn: { write_file: true },     // Human-in-the-loop config
  skills: ["/path/to/skills/"],     // Skill directories
  checkpointer: new MemorySaver(),  // Required for interrupts
  store: new InMemoryStore()        // For long-term memory
});
```
