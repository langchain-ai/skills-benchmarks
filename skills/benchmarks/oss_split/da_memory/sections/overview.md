Deep agents support two types of memory:

**Short-term (StateBackend)**: Persists within a single thread, lost when thread ends
**Long-term (StoreBackend)**: Persists across threads and sessions

Use **CompositeBackend** for hybrid storage: mix ephemeral and persistent files.
