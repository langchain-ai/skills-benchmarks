### What You CAN Configure

- Choose checkpointer implementation
- Specify thread IDs for conversation isolation
- Retrieve/update state at any checkpoint
- Use stores for cross-thread memory

### What You CANNOT Configure

- Checkpoint timing (happens every super-step)
- Share short-term memory across threads
- Skip checkpointer for persistence features
