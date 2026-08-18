The LangGraph Graph API allows you to define agent workflows as directed graphs composed of **nodes** (functions) and **edges** (control flow). This provides fine-grained control over agent orchestration.

**Core Components:**
- **StateGraph**: Main class for building stateful graphs
- **Nodes**: Functions that perform work and update state
- **Edges**: Define execution order (static or conditional)
- **START/END**: Special nodes marking graph entry and exit points
- **Command**: Combine state updates with dynamic routing
