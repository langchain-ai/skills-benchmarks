"""A multi-agent system with persistent memory for user preferences - FIXED VERSION.

All bugs from the broken version have been fixed.
"""

from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend


@tool
def search_papers(query: str) -> str:
    """Search for academic papers."""
    return f"Found papers about: {query}"


@tool
def analyze_data(data: str) -> str:
    """Analyze provided data."""
    return f"Analysis: {data[:50]}..."


@tool
def deploy_to_prod(service: str) -> str:
    """Deploy a service to production."""
    return f"Deployed {service} to production"


@tool
def run_tests(service: str) -> str:
    """Run tests for a service."""
    return f"All tests passed for {service}"


def create_agent_system():
    """Create the multi-agent system with memory and subagents."""

    store = InMemoryStore()

    # FIX: Simplified routes - only persistent storage, no nested ephemeral
    def backend_factory(rt):
        return CompositeBackend(
            default=StateBackend(rt),
            routes={
                "/memory/": StoreBackend(rt),
            },
        )

    # Create the main agent with subagents
    agent = create_deep_agent(
        backend=backend_factory,
        store=store,
        skills=["/project-docs/", "/coding-standards/"],
        # FIX: Add checkpointer for interrupt_on to work
        checkpointer=MemorySaver(),
        subagents=[
            {
                "name": "researcher",
                "description": "Research papers and documentation",
                "system_prompt": "Find relevant papers and summarize findings",
                "tools": [search_papers, analyze_data],
                # FIX: Explicit skills - custom subagents don't inherit
                "skills": ["/project-docs/", "/coding-standards/"],
            },
            {
                "name": "deployer",
                "description": "Deploy services to production after approval",
                "system_prompt": "Deploy services safely, always get approval first",
                "tools": [run_tests, deploy_to_prod],
                "interrupt_on": {"deploy_to_prod": True},
                # FIX: Explicit skills for deployer too
                "skills": ["/project-docs/"],
            },
        ],
    )

    return agent


def save_user_preferences(agent, user_id: str, preferences: dict):
    """Save user preferences for cross-session persistence."""
    config = {"configurable": {"thread_id": f"user-{user_id}"}}

    # FIX: Save to /memory/ directly, not /memory/cache/
    agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"Save these preferences to /memory/prefs-{user_id}.json: {preferences}",
                }
            ]
        },
        config=config,
    )


def load_user_preferences(agent, user_id: str):
    """Load user preferences from persistent storage."""
    config = {"configurable": {"thread_id": f"user-{user_id}"}}

    # FIX: Read from /memory/ directly
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"Read preferences from /memory/prefs-{user_id}.json",
                }
            ]
        },
        config=config,
    )

    return result


def research_topic(agent, topic: str):
    """Have the researcher subagent investigate a topic."""
    config = {"configurable": {"thread_id": "research-session"}}

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"Use the researcher to find information about: {topic}",
                }
            ]
        },
        config=config,
    )

    return result


def deploy_service(agent, service: str):
    """Deploy a service using the deployer subagent."""
    config = {"configurable": {"thread_id": "deploy-session"}}

    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": f"Use the deployer to deploy {service} to production"}
            ]
        },
        config=config,
    )

    return result
