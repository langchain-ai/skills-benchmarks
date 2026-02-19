"""A chat application with tool-calling capabilities.

Issues reported by users:
- "The agent never uses the search or calculator tools, it just makes up answers"
- "When I ask for the current time, the app crashes with a serialization error"
- "The output appears all at once instead of character by character"
- "Sometimes the app crashes with weird AttributeError about tuples"
- "Follow-up questions don't show any response, only the first message works"
"""

from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.tools import tool


@tool
def do_search(s: str) -> str:
    """Tool for searching."""
    return f"Search results for: {s}"


@tool
def calc(x: str) -> str:
    """Calculator."""
    try:
        # Safe eval with limited operations
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
def get_time() -> datetime:
    """Get the current time."""
    return datetime.now()


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
        # Cache the stream for efficiency
        self._stream = None

    def chat(self, user_message: str) -> None:
        """Process a user message with streaming output."""
        print(f"\nUser: {user_message}")
        print("Assistant: ", end="")

        # Reuse stream if available
        if self._stream is None:
            self._stream = self.agent.stream(
                {"messages": [{"role": "user", "content": user_message}]},
                stream_mode=["messages"],
            )

        for mode, chunk in self._stream:
            # Print each token
            if chunk.content:
                print(chunk.content, end="")

        print()

    def chat_with_progress(self, user_message: str) -> None:
        """Show both tool progress and response tokens."""
        print(f"\nUser: {user_message}")

        for mode, chunk in self.agent.stream(
            {"messages": [{"role": "user", "content": user_message}]},
            stream_mode=["updates", "messages"],
        ):
            # Show progress for tools, content for responses
            if chunk.content:
                print(f"Token: {chunk.content}")
            elif hasattr(chunk, "tool_calls"):
                print("[Tool being called...]")


def simple_chat(agent, message: str) -> str:
    """Simple streaming chat that returns the response."""
    tokens = []

    for mode, chunk in agent.stream(
        {"messages": [{"role": "user", "content": message}]},
        stream_mode=["messages"],
    ):
        if chunk.content:
            print(chunk.content, end="")
            tokens.append(chunk.content)

    print()
    return "".join(tokens)


async def api_endpoint(agent, message: str) -> str:
    """Async endpoint for web frameworks like FastAPI.

    Users report: "This blocks my entire server when called"
    """
    import asyncio

    tokens = []

    # Use regular stream in async context
    for mode, chunk in agent.stream(
        {"messages": [{"role": "user", "content": message}]},
        stream_mode=["messages"],
    ):
        if chunk.content:
            tokens.append(chunk.content)
        await asyncio.sleep(0)

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

    # Test 3: Follow-up question (users report nothing shows)
    print("\n--- Test 3: Follow-up ---")
    interface.chat("Can you explain that more?")

    # Test 4: Ask for current time (crashes with serialization error)
    print("\n--- Test 4: Time Query ---")
    try:
        interface.chat("What time is it right now?")
    except Exception as e:
        print(f"\nERROR: {e}")

    # Test 5: Multi-mode streaming
    print("\n--- Test 5: Progress Tracking ---")
    try:
        interface.chat_with_progress("Search for Python best practices")
    except AttributeError as e:
        print(f"\nERROR: {e}")
