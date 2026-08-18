What You CAN Configure:
- **Which tools require approval**: Per-tool policies
- **Allowed decision types**: approve, edit, reject
- **Custom interrupt logic**: Conditional interrupts
- **Feedback messages**: Explain rejections
- **Modified arguments**: Edit tool parameters

What You CANNOT Configure:
- **Skip checkpointer**: HITL requires persistence
- **Interrupt after execution**: Must interrupt before
- **Force model to not call tool**: HITL responds after model decides
- **Modify model's decision-making**: Only tool execution
