"""LangChain agent with Tavily web search."""

import os
from dotenv import load_dotenv

load_dotenv()

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor


def run_agent(query: str) -> str:
    """Run the search agent on a query."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [TavilySearchResults(max_results=3)]

    prompt = """
    You are a helpful assistant that can answer questions and help with tasks.
    """
    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    result = executor.invoke({"input": query})
    return result["output"]


if __name__ == "__main__":
    query = "What is LangChain?"
    print(f"\nRunning agent with query: {query}\n")
    print("=" * 53)
    response = run_agent(query)
    print(f"\nAgent response:\n{response}")
