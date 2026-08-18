**What Agents CAN Do:**
- Save files to persistent storage (/memories/)
- Access persisted files across threads
- Organize memory with custom paths
- Mix ephemeral and persistent storage
- Use Store namespace/key pattern directly

**What Agents CANNOT Do:**
- Access memory without proper Store setup
- Share memory across different agents (without shared Store)
- Persist files without StoreBackend configuration
- Access StateBackend files across threads
