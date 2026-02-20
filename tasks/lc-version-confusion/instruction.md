The following file `legacy_agent.py` has version confusion issues common in LangChain codebases. It runs but uses the wrong abstraction level and a deprecated import. Fix it and save to `agent.py`, then run it with the query: "What is LangChain?"

```python
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults  # deprecated
from langgraph.prebuilt import create_react_agent  # wrong function that is out of date for langchain v1
from langchain.tools import tool

llm = ChatOpenAI(model="gpt-4o-mini")
search_tool = TavilySearchResults(max_results=3)

agent = create_react_agent(llm, [search_tool])

if __name__ == "__main__":
    # LangGraph message format — wouldn't be needed with create_agent
    result = agent.invoke({{"messages": [{{"role": "user", "content": "What is LangChain?"}}]}})
    print(result["messages"][-1].content)
```

IMPORTANT: Run files directly (not in background). If code fails after 2 attempts to fix, save the file and report the error - do not enter debug loops.
