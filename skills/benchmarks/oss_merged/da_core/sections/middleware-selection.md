| If you need to... | Middleware | Notes |
|------------------|------------|-------|
| Track complex tasks | TodoListMiddleware | Default enabled |
| Manage file context | FilesystemMiddleware | Configure backend |
| Delegate work | SubAgentMiddleware | Add custom subagents |
| Add human approval | HumanInTheLoopMiddleware | Requires checkpointer |
| Load skills | SkillsMiddleware | Provide skill directories |
| Access memory | MemoryMiddleware | Requires Store instance |
