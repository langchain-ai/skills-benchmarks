| Type | When Set | Use Case |
|------|----------|----------|
| **`interrupt()` (recommended)** | Inside node code | Human-in-the-loop, conditional pausing. Resume with `Command(resume=value)` |
| `interrupt_before` / `interruptBefore` | At compile time | **Debugging only, not for HITL.** Resume with `invoke(None/null, config)` |
| `interrupt_after` / `interruptAfter` | At compile time | **Debugging only, not for HITL.** Resume with `invoke(None/null, config)` |
