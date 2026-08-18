**What Agents CAN Configure**

- Define custom nodes (any function)
- Add static edges between nodes
- Add conditional edges with custom logic
- Use Command for combined state/routing
- Create loops with conditional termination
- Fan-out with Send API (map-reduce)
- Set breakpoints (interrupt_before/after or interruptBefore/After)
- Customize state schema
- Specify checkpointer for persistence

**What Agents CANNOT Configure**

- Modify START/END node behavior
- Change super-step execution model
- Alter message-passing protocol
- Override graph compilation logic
- Bypass state update mechanism
