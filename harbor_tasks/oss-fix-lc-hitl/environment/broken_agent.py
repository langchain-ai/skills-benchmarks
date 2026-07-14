"""A document management agent with approval workflow.

Issues reported by users:
- "Dangerous operations like 'delete' execute without any approval step"
- "After I approve an action, the system starts from scratch instead of continuing"
- "The action history only shows my last action, previous ones disappeared"
- "I can see other users' action history mixed with mine"
"""

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


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

agent = create_agent(
    model=model,
    tools=[lookup_document, create_document, delete_document],
)


def process_request(message: str, thread_id: str = "default") -> dict:
    """Process a user request through the agent."""
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    return result


def resume_after_approval(thread_id: str = "default") -> dict:
    """Resume the agent after human approval of a dangerous action."""
    result = agent.invoke({"messages": [{"role": "user", "content": "I approve the action"}]})
    return result


if __name__ == "__main__":
    print("=== Document Management Agent ===\n")

    print("--- Looking up a document ---")
    result = process_request("Look up the document called 'quarterly_report'")
    print(result["messages"][-1].content)

    print("\n--- Deleting a document (should require approval!) ---")
    result = process_request("Delete the document 'old_drafts'")
    print(result["messages"][-1].content)
