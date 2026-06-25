The `create_agent()`/`createAgent()` function provides a production-ready agent implementation built on LangGraph.

Key Concepts:
- **Agent Loop**: The model decides, calls tools, observes results, repeats until done
- **ReAct Pattern**: Reasoning and Acting - the agent reasons about what to do, then acts by calling tools
- **Graph-based Runtime**: Agents run on a LangGraph graph with nodes (model, tools, middleware) and edges
