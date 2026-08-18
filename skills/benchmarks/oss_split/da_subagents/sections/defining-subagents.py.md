Define subagent with custom tools:

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
