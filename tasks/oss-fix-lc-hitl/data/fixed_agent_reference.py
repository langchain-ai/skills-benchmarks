"""A document management agent with approval workflow - FIXED VERSION.

All bugs from the broken version have been fixed.
"""

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command


@tool
def lookup_document(name: str) -> str:
    """Look up a document by name and return its metadata.

    Args:
        name: The document name to look up
    """
    return f"Document '{name}': 3 pages, last modified 2024-01-15, owner: admin"


@tool
def create_document(name: str, content: str) -> str:
    """Create a new document with the given name and content.

    Args:
        name: Name for the new document
        content: Content to write
    """
    return f"Created document '{name}' with {len(content)} characters"


@tool
def delete_document(name: str) -> str:
    """Delete a document permanently. This is a dangerous operation that cannot be undone.

    Args:
        name: The document to delete
    """
    return f"Permanently deleted document '{name}'"


model = ChatOpenAI(model="gpt-4.1")

# FIX 1: Added MemorySaver checkpointer for state persistence
checkpointer = MemorySaver()

# FIX 2: Added HITL middleware to gate dangerous tools
agent = create_agent(
    model=model,
    tools=[lookup_document, create_document, delete_document],
    checkpointer=checkpointer,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "delete_document": True,
            }
        )
    ],
)


def process_request(message: str, thread_id: str = "default") -> dict:
    """Process a user request through the agent."""
    # FIX 3: Pass thread_id config for state tracking
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke({"messages": [{"role": "user", "content": message}]}, config=config)
    return result


def resume_after_approval(thread_id: str = "default") -> dict:
    """Resume the agent after human approval of a dangerous action."""
    # FIX 4: Use Command(resume=...) to continue from checkpoint
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
    return result


if __name__ == "__main__":
    print("=== Document Management Agent ===\n")

    # Test 1: Safe operation (completes without approval)
    print("--- Looking up a document ---")
    result = process_request("Look up the document called 'quarterly_report'", thread_id="demo")
    print(result["messages"][-1].content)

    # Test 2: Dangerous operation (requires approval)
    print("\n--- Deleting a document (requires approval) ---")
    result = process_request("Delete the document 'old_drafts'", thread_id="demo-delete")
    if "__interrupt__" in result:
        print("INTERRUPTED: Waiting for human approval...")
        print(f"Tool call: {result['__interrupt__'][0].value}")

        # Approve and resume
        result = resume_after_approval(thread_id="demo-delete")
        print(result["messages"][-1].content)
    else:
        print(result["messages"][-1].content)
