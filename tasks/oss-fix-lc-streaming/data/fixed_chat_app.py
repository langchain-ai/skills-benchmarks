"""A chat application with tool-calling capabilities - FIXED VERSION.

All LangChain-specific bugs from the broken version have been fixed.
"""

from datetime import datetime

from langchain.tools import tool
from langchain_openai import ChatOpenAI


# FIX: Added proper docstring and type hint
@tool
def do_search(s: str) -> str:
    """Search the web for information on any topic.

    Use this tool when the user asks about current events, news,
    facts, or any information that might require looking up.

    Args:
        s: The search query or topic to search for
    """
    return f"Search results for: {s}"


# FIX: Added descriptive docstring and type hint
@tool
def calc(x: str) -> str:
    """Perform mathematical calculations and computations.

    Use this tool when the user asks to calculate, compute, or
    do math operations like addition, subtraction, multiplication,
    or division.

    Args:
        x: A mathematical expression to evaluate (e.g., "15 * 7 + 23")
    """
    try:
        allowed = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,
        }
        return str(eval(x, {"__builtins__": {}}, allowed))
    except Exception as e:
        return f"Error: {e}"


@tool
def get_time() -> str:
    """Get the current time and date.

    Use this when the user asks for the current time, today's date,
    or needs to know what day it is.
    """
    return datetime.now().isoformat()


def create_agent():
    """Create an agent with tools."""
    from langchain.agents import create_agent

    model = ChatOpenAI(model="gpt-4.1", streaming=True)
    agent = create_agent(
        model=model,
        tools=[do_search, calc, get_time],
    )
    return agent


class ChatInterface:
    """Interactive chat interface with streaming output."""

    def __init__(self):
        self.agent = create_agent()

    def chat(self, user_message: str) -> None:
        """Process a user message with streaming output."""
        print(f"\nUser: {user_message}")
        print("Assistant: ", end="")

        stream = self.agent.stream(
            {"messages": [{"role": "user", "content": user_message}]},
            stream_mode=["messages"],
        )

        for mode, chunk in stream:
            # FIX: Unpack the (token, metadata) tuple from messages mode
            token, _metadata = chunk
            if token.content:
                print(token.content, end="", flush=True)

        print()

    def chat_with_progress(self, user_message: str) -> None:
        """Show both tool progress and response tokens."""
        print(f"\nUser: {user_message}")

        for mode, chunk in self.agent.stream(
            {"messages": [{"role": "user", "content": user_message}]},
            stream_mode=["updates", "messages"],
        ):
            # FIX: Check mode before processing - different modes have different formats
            if mode == "messages":
                token, _metadata = chunk
                if token.content:
                    print(f"Token: {token.content}")
            elif mode == "updates":
                if hasattr(chunk, "tool_calls"):
                    print("[Tool being called...]")


def simple_chat(agent, message: str) -> str:
    """Simple streaming chat that returns the response."""
    tokens = []

    for mode, chunk in agent.stream(
        {"messages": [{"role": "user", "content": message}]},
        stream_mode=["messages"],
    ):
        # FIX: Unpack tuple
        token, _metadata = chunk
        if token.content:
            print(token.content, end="", flush=True)
            tokens.append(token.content)

    print()
    return "".join(tokens)


async def api_endpoint(agent, message: str) -> str:
    """Async endpoint for web frameworks like FastAPI."""
    tokens = []

    # FIX: Use astream in async context to avoid blocking event loop
    async for mode, chunk in agent.astream(
        {"messages": [{"role": "user", "content": message}]},
        stream_mode=["messages"],
    ):
        token, _metadata = chunk
        if token.content:
            tokens.append(token.content)

    return "".join(tokens)
