| Need | Python Solution | TypeScript Solution | Use Case |
|------|-----------------|---------------------|----------|
| Overwrite value | No reducer (default) | Plain Zod schema | Simple fields like strings |
| Append to list | `operator.add` | `ReducedValue` with concat | Message history, logs |
| Custom logic | Custom reducer function | Custom reducer function | Complex merging, validation |
| Messages | `Annotated[list, add_messages]` | `MessagesValue` | Chat applications |
