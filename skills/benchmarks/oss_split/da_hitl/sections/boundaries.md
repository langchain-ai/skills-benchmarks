**What Agents CAN Configure:**
- Which tools require approval
- Allowed decision types per tool
- Custom interrupt descriptions
- Checkpointer implementation
- Interrupt handling logic

**What Agents CANNOT Configure:**
- The HITL protocol (approve/edit/reject structure)
- Skip checkpointer requirement
- Interrupt without saving state
- Have subagents interrupt without main checkpointer
