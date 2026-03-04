---
name: deep-agents-subagents-py
description: "[Deep Agents] Using SubAgentMiddleware to spawn subagents for task delegation, context isolation, and specialized work in Deep Agents."
---

<overview>
SubAgentMiddleware enables agents to delegate work to specialized subagents via the `task` tool. Subagents provide:
- **Context isolation**: Subagent work doesn't clutter main agent's context
- **Specialization**: Different tools/prompts for specific tasks
- **Token efficiency**: Large subtask context compressed into single result
- **Parallel execution**: Multiple subagents can run concurrently
</overview>

<when-to-use-subagents>

| Use Subagents When | Use Main Agent When |
|-------------------|-------------------|
| Task needs specialized tools | General-purpose tools sufficient |
| Want to isolate complex multi-step work | Single-step operation |
| Need clean context for main agent | Context bloat acceptable |
| Task benefits from different model/prompt | Same config works |

</when-to-use-subagents>

<how-it-works>
Main agent has `task` tool -> creates fresh subagent -> subagent executes autonomously -> returns final report to main agent.

**Default subagent**: "general-purpose" - automatically available with same tools/config as main agent.
</how-it-works>

<subagent-patterns>

| Pattern | When to Use | Example |
|---------|------------|---------|
| Specialized tools | Task needs unique tools | code-reviewer with linting tools |
| Different model | Cost/capability tradeoff | GPT-4 main, GPT-3.5 for simple subagents |
| Context isolation | Keep main context clean | web-research dumps to files, returns summary |
| Parallel work | Independent subtasks | analyze-data + generate-report simultaneously |

</subagent-patterns>

<ex-dictionary-based-subagent>
```python
from deepagents import create_deep_agent
from langchain.tools import tool

@tool
def search_papers(query: str) -> str:
    """Search academic papers."""
    return f"Found 10 papers about {query}"

@tool
def summarize_paper(paper_id: str) -> str:
    """Summarize a research paper."""
    return f"Summary of paper {paper_id}"

agent = create_deep_agent(
    subagents=[
        {
            "name": "research",
            "description": "Research academic papers and provide summaries",
            "system_prompt": "You are a research assistant. Search papers and provide concise summaries.",
            "tools": [search_papers, summarize_paper],
            "model": "claude-sonnet-4-5-20250929",  # Optional: override model
        }
    ]
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Research recent papers on transformers"}]
})
# Main agent calls: task(agent="research", instruction="Research recent papers on transformers")
```
</ex-dictionary-based-subagent>

<ex-compiled-subagent>
```python
from deepagents import create_deep_agent, CompiledSubAgent
from langgraph.graph import StateGraph

def create_weather_graph():
    workflow = StateGraph(...)
    # Build custom graph
    return workflow.compile()

weather_graph = create_weather_graph()

weather_subagent = CompiledSubAgent(
    name="weather",
    description="Get weather forecasts for cities",
    runnable=weather_graph
)

agent = create_deep_agent(
    subagents=[weather_subagent]
)
```
</ex-compiled-subagent>

<ex-research-subagent>
```python
from deepagents import create_deep_agent
from langchain.tools import tool

@tool
def web_search(query: str) -> str:
    """Search the web."""
    return f"Search results for: {query}"

@tool
def analyze_data(data: str) -> str:
    """Analyze data and extract insights."""
    return f"Analysis: {data[:100]}..."

agent = create_deep_agent(
    subagents=[
        {
            "name": "researcher",
            "description": "Conduct web research and compile findings",
            "system_prompt": "Search thoroughly, save results to /research/ directory, return concise summary",
            "tools": [web_search],
        },
        {
            "name": "analyst",
            "description": "Analyze data and provide insights",
            "system_prompt": "Provide data-driven insights with specific numbers",
            "tools": [analyze_data],
        }
    ]
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Research market trends for EVs, then analyze the data"
    }]
})
# Main agent: task(agent="researcher", ...) -> task(agent="analyst", ...)
```
</ex-research-subagent>

<ex-subagent-with-hitl>
```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    subagents=[
        {
            "name": "code-deployer",
            "description": "Deploy code to production",
            "system_prompt": "Deploy code safely with all checks",
            "tools": [run_tests, deploy_to_prod],
            "interrupt_on": {"deploy_to_prod": True},  # Require approval
        }
    ],
    checkpointer=MemorySaver()  # Required for interrupts
)
```
</ex-subagent-with-hitl>

<ex-subagent-with-custom-skills>
```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    skills=["/main-skills/"],  # Main agent skills
    subagents=[
        {
            "name": "python-expert",
            "description": "Python code review and refactoring",
            "system_prompt": "Review Python code for best practices",
            "tools": [read_code, suggest_improvements],
            "skills": ["/python-skills/"],  # Subagent-specific skills
        }
    ]
)
# Note: Custom subagents DON'T inherit main agent's skills by default
# General-purpose subagent DOES inherit main agent's skills
```
</ex-subagent-with-custom-skills>

<ex-default-general-purpose-subagent>
```python
from deepagents import create_deep_agent

agent = create_deep_agent()

# Agent can use default "general-purpose" subagent for context isolation
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Analyze this large dataset and summarize the key findings"
    }]
})
# Agent may call: task(instruction="Analyze dataset and summarize")
# Uses general-purpose subagent with same tools/config as main
```
</ex-default-general-purpose-subagent>

<boundaries>
### What Agents CAN Configure

- Subagent name and description
- Custom tools for subagents
- Different models per subagent
- Subagent-specific system prompts
- Subagent middleware and skills
- Human-in-the-loop for subagent tools

### What Agents CANNOT Configure

- Change the `task` tool name
- Make subagents stateful (they're ephemeral)
- Share state directly between subagents
- Remove the default general-purpose subagent
- Have subagents call back to main agent
</boundaries>

<fix-subagents-are-stateless>
```python
# WRONG: Subagents don't remember previous calls
agent.invoke({"messages": [{"role": "user", "content": "task(agent='research', instruction='Find data')"}]})
agent.invoke({"messages": [{"role": "user", "content": "task(agent='research', instruction='What did you find?')"}]})
# Second call won't remember first call - fresh subagent each time

# CORRECT: Main agent maintains conversation memory, not subagents
```
</fix-subagents-are-stateless>

<fix-custom-subagents-dont-inherit-skills>
```python
# WRONG: Subagent won't have main agent's skills
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{"name": "helper", ...}]  # No skills
)

# CORRECT: Explicitly provide skills to subagent
agent = create_deep_agent(
    skills=["/main-skills/"],
    subagents=[{
        "name": "helper",
        "skills": ["/helper-skills/"],  # Subagent-specific
        ...
    }]
)

# CORRECT: General-purpose subagent DOES inherit main skills
# agent.invoke() -> task(instruction="...") uses general-purpose with main skills
```
</fix-custom-subagents-dont-inherit-skills>

<fix-subagent-results-are-final>
```python
# Subagents return a single final message
# They can't have back-and-forth dialogue with main agent

# WRONG: Can't do this:
# Main: "task(agent='research', instruction='Find data')"
# Research: "What topic?"
# Main: "AI"
# Research: "Here's AI data"

# CORRECT: Provide complete instructions upfront
# Main: "task(agent='research', instruction='Find data on AI, save to /research/, return summary')"
```
</fix-subagent-results-are-final>

<fix-subagent-interrupts-require-main-checkpointer>
```python
# WRONG: Subagent HITL without checkpointer
agent = create_deep_agent(
    subagents=[{
        "name": "deployer",
        "interrupt_on": {"deploy": True}
    }]
)

# CORRECT: Checkpointer on main agent, not subagent
agent = create_deep_agent(
    subagents=[{
        "name": "deployer",
        "interrupt_on": {"deploy": True}
    }],
    checkpointer=MemorySaver()  # On main agent
)
```
</fix-subagent-interrupts-require-main-checkpointer>

<links>
- [Subagents Guide](https://docs.langchain.com/oss/python/deepagents/subagents)
- [SubAgent Middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in#subagent)
- [Task Delegation](https://docs.langchain.com/oss/python/deepagents/harness#task-delegation-subagents)
</links>
