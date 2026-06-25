| If you need to... | Use this middleware | When to customize |
|------------------|-------------------|------------------|
| Track complex multi-step tasks | TodoListMiddleware / todoListMiddleware | Default works; customize prompt if needed |
| Manage file context | FilesystemMiddleware / createFilesystemMiddleware | Change backend or tool descriptions |
| Delegate specialized work | SubAgentMiddleware / createSubAgentMiddleware | Add custom subagents with specific tools |
| Prevent context overflow | SummarizationMiddleware / summarizationMiddleware | Default works; customize summarization strategy |
| Cache prompts (Anthropic) | AnthropicPromptCachingMiddleware / anthropicPromptCachingMiddleware | Default works automatically |
| Add human approval | HumanInTheLoopMiddleware / humanInTheLoopMiddleware | Configure which tools require approval |
| Load skills on-demand | SkillsMiddleware / skillsMiddleware | Provide skill directories |
| Access persistent memory | MemoryMiddleware / memoryMiddleware | Provide a Store instance |
