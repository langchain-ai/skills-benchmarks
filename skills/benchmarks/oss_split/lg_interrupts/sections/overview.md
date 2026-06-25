Interrupts enable human-in-the-loop patterns by pausing graph execution for external input. LangGraph saves state and waits indefinitely until you resume execution.

**Key Types:**
- **Dynamic Interrupts**: `interrupt()` function called in nodes
- **Static Breakpoints**: `interrupt_before`/`interrupt_after` (Python) or `interruptBefore`/`interruptAfter` (TypeScript) at compile time
