"""A chat application with tool-calling capabilities.

Issues reported by users:
- "The agent never uses the search or calculator tools, it just makes up answers"
- "The search tool has terrible accuracy - it searches for wrong things"
- "Sometimes the app crashes with weird AttributeError about tuples"
- "The progress tracking mode shows errors instead of proper updates"
- "The async API endpoint blocks my entire server"
"""

from datetime import datetime

from langchain.tools import tool
from langchain_openai import ChatOpenAI


@tool
def do_search(s):
    return f"Search results for: {s}"


@tool
def calc(x):
    """Math."""
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

        for _mode, chunk in stream:
            if chunk.content:
                print(chunk.content, end="", flush=True)

        print()

    def chat_with_progress(self, user_message: str) -> None:
        """Show both tool progress and response tokens."""
        print(f"\nUser: {user_message}")

        for _mode, chunk in self.agent.stream(
            {"messages": [{"role": "user", "content": user_message}]},
            stream_mode=["updates", "messages"],
        ):
            if chunk.content:
                print(f"Token: {chunk.content}")
            elif hasattr(chunk, "tool_calls"):
                print("[Tool being called...]")


def simple_chat(agent, message: str) -> str:
    """Simple streaming chat that returns the response."""
    tokens = []

    for _mode, chunk in agent.stream(
        {"messages": [{"role": "user", "content": message}]},
        stream_mode=["messages"],
    ):
        if chunk.content:
            print(chunk.content, end="", flush=True)
            tokens.append(chunk.content)

    print()
    return "".join(tokens)


async def api_endpoint(agent, message: str) -> str:
    """Async endpoint for web frameworks like FastAPI.

    Users report: "This blocks my entire server when called"
    """
    tokens = []

    for _mode, chunk in agent.stream(
        {"messages": [{"role": "user", "content": message}]},
        stream_mode=["messages"],
    ):
        if chunk.content:
            tokens.append(chunk.content)

    return "".join(tokens)


if __name__ == "__main__":
    print("=" * 60)
    print("Chat Application Demo")
    print("=" * 60)

    interface = ChatInterface()

    # Test 1: Ask about something (agent should use search tool)
    print("\n--- Test 1: Information Query ---")
    interface.chat("What are the latest developments in AI?")

    # Test 2: Ask a math question (agent should use calculator)
    print("\n--- Test 2: Math Query ---")
    interface.chat("What is 15 * 7 + 23?")

    # Test 3: Ask for current time
    print("\n--- Test 3: Time Query ---")
    interface.chat("What time is it right now?")

    # Test 4: Multi-mode streaming
    print("\n--- Test 4: Progress Tracking ---")
    try:
        interface.chat_with_progress("Search for Python best practices")
    except AttributeError as e:
        print(f"\nERROR: {e}")
