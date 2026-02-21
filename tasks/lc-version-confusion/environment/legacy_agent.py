from langchain_community.tools.tavily_search import TavilySearchResults  # deprecated
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent  # wrong level for a simple agent

llm = ChatOpenAI(model="gpt-4o-mini")
search_tool = TavilySearchResults(max_results=3)

# create_react_agent is LangGraph's lower-level primitive — fine when you need
# custom graph control, but adds unnecessary complexity for a simple tool-calling agent
agent = create_react_agent(llm, [search_tool])

if __name__ == "__main__":
    # LangGraph message format — wouldn't be needed with create_agent
    result = agent.invoke({"messages": [{"role": "user", "content": "What is LangChain?"}]})
    print(result["messages"][-1].content)
