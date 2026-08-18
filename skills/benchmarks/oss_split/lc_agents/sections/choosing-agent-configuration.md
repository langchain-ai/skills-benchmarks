| Need | Configuration | Example |
|------|---------------|---------|
| Basic agent with tools | `create_agent(model, tools)` | Search, calculator, weather |
| Custom system instructions | Add `system_prompt` | Domain-specific behavior |
| Human approval for sensitive operations | Add human-in-the-loop middleware | Database writes, emails |
| Persistence across sessions | Add `checkpointer` | Multi-turn conversations |
| Structured output format | Add `response_format` | Extract contact info, parse forms |
