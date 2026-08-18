### What You CAN Configure

- Define custom state schemas with TypedDict/StateSchema
- Add reducers to control how state updates are merged
- Create nodes (any function)
- Add static and conditional edges
- Use Command for combined state/routing
- Create loops with conditional termination

### What You CANNOT Configure

- Modify START/END behavior
- Change the Pregel execution model
- Access state outside node functions
- Modify state directly (must return updates)
