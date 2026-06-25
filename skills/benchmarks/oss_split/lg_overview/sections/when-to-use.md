**When to Use LangGraph**

LangGraph is ideal when you need:
- Fine-grained control over agent orchestration
- Durable execution for long-running, stateful agents
- Complex workflows combining deterministic and agentic steps
- Production infrastructure for agent deployment
- Human-in-the-loop workflows
- Persistent state across multiple interactions

**When NOT to Use LangGraph**

Consider alternatives when you:
- Need a quick start with pre-built architectures -> Use **LangChain agents**
- Want batteries-included features (automatic compression, virtual filesystem) -> Use **Deep Agents**
- Have simple, stateless LLM workflows -> Use **LangChain** directly
- Don't need state persistence or complex orchestration
