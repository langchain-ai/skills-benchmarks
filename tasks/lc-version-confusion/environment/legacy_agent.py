"""Legacy LangChain agent using 0.1/0.2 era patterns.

This file uses deprecated APIs that need to be modernized.
DO NOT run this file directly - it uses outdated imports that won't work with LangChain 1.0.
"""

# LEGACY: old chat_models import path (removed in 1.0)
from langchain.chat_models import ChatOpenAI  # noqa: F401 - deprecated

# LEGACY: old tools import path
from langchain.tools import Tool  # noqa: F401 - deprecated

# LEGACY: old agents module paths
from langchain.agents import AgentExecutor, initialize_agent  # noqa: F401 - deprecated
from langchain.agents import AgentType  # noqa: F401 - deprecated

# LEGACY: old LLMChain
from langchain.chains import LLMChain  # noqa: F401 - deprecated

# LEGACY: old prompt template location
from langchain.prompts import PromptTemplate  # noqa: F401 - may still work but wrong path


def get_word_length(word: str) -> str:
    """Return the length of a word."""
    return str(len(word))


# LEGACY: Tool() constructor pattern instead of @tool decorator
word_length_tool = Tool(
    name="word_length",
    func=get_word_length,
    description="Returns the length of a word",
)

# LEGACY: initialize_agent with AgentType enum
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent_executor = initialize_agent(
    tools=[word_length_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

if __name__ == "__main__":
    result = agent_executor.invoke({"input": "What tools do you have available?"})
    print(result["output"])
