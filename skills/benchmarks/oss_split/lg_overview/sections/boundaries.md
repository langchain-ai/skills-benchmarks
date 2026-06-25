**What Agents CAN Configure/Control**

- **Node Logic**: Define any function as a node
- **State Schema**: Customize state structure and reducers
- **Control Flow**: Add conditional edges, loops, branching
- **Persistence Layer**: Choose checkpointer (InMemory/MemorySaver, SQLite, Postgres)
- **Streaming Modes**: Configure what data to stream
- **Interrupts**: Add human-in-the-loop at any point
- **Recursion Limits**: Control maximum execution steps
- **Tools and Models**: Use any LLM or tool provider

**What Agents CANNOT Configure/Control**

- **Core Graph Execution Model**: Pregel-based runtime is fixed
- **Super-step Behavior**: Cannot change how nodes are batched
- **Message Passing Protocol**: Internal communication is predefined
- **Checkpoint Schema**: Internal checkpoint format is fixed
- **Graph Compilation**: Cannot modify compilation logic
