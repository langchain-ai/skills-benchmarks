| Type | When Set | Use Case |
|------|----------|----------|
| **`interrupt()` (recommended)** | Inside node code | Human-in-the-loop, conditional pausing. Resume with `Command(resume=value)` |
| `interrupt_before` | At compile time | **Debugging only, not for HITL.** Resume with `invoke(None, config)` |
| `interrupt_after` | At compile time | **Debugging only, not for HITL.** Resume with `invoke(None, config)` |
