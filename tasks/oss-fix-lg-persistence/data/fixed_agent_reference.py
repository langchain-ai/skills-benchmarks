"""Fixed version of the LangGraph chatbot agent.

Fixes applied:
1. Added checkpointer to compile() for persistence
2. Uses thread_id when invoking for conversation isolation
3. Added Annotated[list, operator.add] reducer for messages
"""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated
import operator
from langchain_core.tools import tool


class State(TypedDict):
    """Agent state for tracking conversations."""
    # FIX: Added reducer so messages accumulate instead of overwrite
    messages: Annotated[list, operator.add]
    context: dict
    current_step: str


@tool
def lookup_order(order_id: str) -> str:
    """Look up order status by ID."""
    return f"Order {order_id}: Shipped, arriving in 2 days"


def extract_context(state: State) -> dict:
    """Extract user context from messages."""
    messages = state.get("messages", [])
    context = state.get("context", {})

    for msg in messages:
        if isinstance(msg, str):
            lower_msg = msg.lower()
            if "my name is" in lower_msg:
                name = lower_msg.split("my name is")[-1].strip().split()[0]
                context["name"] = name.title()

    return {"context": context, "current_step": "extracted"}


def generate_response(state: State) -> dict:
    """Generate a response based on conversation history and context."""
    messages = state.get("messages", [])
    context = state.get("context", {})

    if not messages:
        return {"messages": ["Hello! How can I help you today?"]}

    last_message = messages[-1] if messages else ""
    response = f"I heard: {last_message}"

    if isinstance(last_message, str):
        if "name" in last_message.lower() and "what" in last_message.lower():
            if context.get("name"):
                response = f"Your name is {context['name']}!"
            else:
                response = "I don't know your name yet. What is it?"
        elif "order" in last_message.lower():
            response = "I can help with that. What's your order ID?"

    return {"messages": [response], "current_step": "responded"}


def route_message(state: State) -> str:
    """Route to appropriate handler."""
    return "respond"


# Build the conversation graph
builder = StateGraph(State)
builder.add_node("extract", extract_context)
builder.add_node("respond", generate_response)

builder.add_edge(START, "extract")
builder.add_edge("extract", "respond")
builder.add_conditional_edges(
    "respond",
    route_message,
    {"respond": END}
)

# FIX: Add checkpointer at compile time
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)


def chat(user_message: str, thread_id: str = "default") -> str:
    """Process a user message and return the bot's response.

    FIX: Added thread_id parameter for conversation isolation.
    """
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke({
        "messages": [user_message],
        "context": {},
        "current_step": "start"
    }, config)

    responses = result.get("messages", [])
    return responses[-1] if responses else "Sorry, I couldn't process that."


if __name__ == "__main__":
    print("Customer Support Bot (Fixed)")
    print("-" * 40)

    print("\nUser: Hi! My name is Sarah")
    print(f"Bot: {chat('Hi! My name is Sarah', thread_id='session-1')}")

    print("\nUser: What is my name?")
    print(f"Bot: {chat('What is my name?', thread_id='session-1')}")

    print("\nUser: I have a question about my order")
    print(f"Bot: {chat('I have a question about my order', thread_id='session-1')}")
