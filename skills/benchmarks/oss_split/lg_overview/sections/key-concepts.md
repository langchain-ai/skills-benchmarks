**1. Graph-Based Execution Model**

LangGraph models agent workflows as **graphs** with three core components:

- **State**: Shared data structure representing the current snapshot of your application
- **Nodes**: Functions that encode agent logic and update state
- **Edges**: Determine which node executes next (can be conditional or fixed)

**2. Core Capabilities**

| Capability | Description |
|-----------|-------------|
| **Durable Execution** | Agents persist through failures and resume from checkpoints |
| **Streaming** | Real-time updates during execution (state, tokens, custom data) |
| **Human-in-the-loop** | Pause execution for human review and intervention |
| **Persistence** | Thread-level and cross-thread state management |
| **Time Travel** | Resume from any checkpoint in execution history |

**3. Message Passing Model**

Inspired by Google's Pregel system:
- Execution proceeds in discrete "super-steps"
- Nodes execute in parallel within a super-step
- Sequential nodes belong to separate super-steps
- Graph terminates when all nodes are inactive
