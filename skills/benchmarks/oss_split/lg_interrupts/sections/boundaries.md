**What You CAN Configure**

- Call `interrupt()` anywhere in nodes
- Set compile-time breakpoints
- Resume with `Command(resume=...)` or `new Command({ resume: ... })`
- Edit state during interrupts
- Stream while handling interrupts
- Conditional interrupt logic

**What You CANNOT Configure**

- Interrupt without checkpointer
- Modify interrupt mechanism
- Resume without thread_id
