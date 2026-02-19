"""A LangGraph chatbot agent for handling customer inquiries.

Issues reported by users:
- "The bot forgets what I said earlier in the same conversation"
- "Sometimes my messages just disappear"
- "When I come back later, it doesn't remember our previous chat"
"""

from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


class State(TypedDict):
    """Agent state for tracking conversations."""
    messages: list  # Conversation history
    context: dict  # User context (name, preferences, etc.)
    current_step: str


@tool
def lookup_order(order_id: str) -> str:
    """Look up order status by ID."""
    # Simulated order lookup
    return f"Order {order_id}: Shipped, arriving in 2 days"


def extract_context(state: State) -> State:
    """Extract user context from messages."""
    messages = state.get("messages", [])
    context = state.get("context", {})

    for msg in messages:
        if isinstance(msg, str):
            lower_msg = msg.lower()
            if "my name is" in lower_msg:
                name = lower_msg.split("my name is")[-1].strip().split()[0]
                context["name"] = name.title()

    # Update state and return it
    state["context"] = context
    state["current_step"] = "extracted"
    return state


def generate_response(state: State) -> dict:
    """Generate a response based on conversation history and context."""
    messages = state.get("messages", [])
    context = state.get("context", {})

    if not messages:
        return {"messages": ["Hello! How can I help you today?"]}

    last_message = messages[-1] if messages else ""
    response = f"I heard: {last_message}"

    # Check for name queries
    if isinstance(last_message, str):
        if "name" in last_message.lower() and "what" in last_message.lower():
            if context.get("name"):
                response = f"Your name is {context['name']}!"
            else:
                response = "I don't know your name yet. What is it?"

        # Check for order queries
        elif "order" in last_message.lower():
            response = "I can help with that. What's your order ID?"

    return {"messages": [response], "current_step": "responded"}


def route_message(state: State) -> str:
    """Route to appropriate handler."""
    messages = state.get("messages", [])
    if not messages:
        return "respond"

    last_message = messages[-1] if messages else ""
    if isinstance(last_message, str) and "order" in last_message.lower():
        # Could route to order lookup, but for now just respond
        pass

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
    {"respond": END}  # Only one path, could be more flexible
)

# Compile without persistence - every conversation is fresh
graph = builder.compile()


def chat(user_message: str) -> str:
    """Process a user message and return the bot's response.

    Note: Each call starts fresh - no memory of previous calls.
    """
    result = graph.invoke({
        "messages": [user_message],
        "context": {},
        "current_step": "start"
    })

    responses = result.get("messages", [])
    return responses[-1] if responses else "Sorry, I couldn't process that."


if __name__ == "__main__":
    print("Customer Support Bot")
    print("-" * 40)

    # Conversation that should work but doesn't
    print("\nUser: Hi! My name is Sarah")
    print(f"Bot: {chat('Hi! My name is Sarah')}")

    print("\nUser: What's my name?")
    print(f"Bot: {chat('What is my name?')}")

    print("\nUser: I have a question about my order")
    print(f"Bot: {chat('I have a question about my order')}")
