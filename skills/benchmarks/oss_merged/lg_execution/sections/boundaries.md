### What You CAN Configure

- Choose workflow vs agent pattern
- Use Send API for parallel execution
- Call `interrupt()` anywhere in nodes
- Set compile-time breakpoints
- Resume with `Command(resume=...)`
- Choose stream modes

### What You CANNOT Configure

- Interrupt without checkpointer
- Resume without thread_id
- Change Send API message-passing model
