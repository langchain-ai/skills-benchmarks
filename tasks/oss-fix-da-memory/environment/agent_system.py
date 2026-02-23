"""A multi-agent system with persistent memory for user preferences.

Issues reported by users:
- "My preferences are lost when I restart the app"
- "Some files persist but others don't, seems random"
- "The research subagent doesn't have access to our documentation skills"
- "The deployment approval feature doesn't work - it deploys without asking"
"""

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langchain.tools import tool
from langgraph.store.memory import InMemoryStore


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

    # Configure backend with multiple storage paths
    # Intention: /memory/ for long-term, /memory/cache/ for temporary
    def backend_factory(rt):
        return CompositeBackend(
            default=StateBackend(rt),
            routes={
                "/memory/": StoreBackend(rt),
                "/memory/cache/": StateBackend(rt),  # Temp cache under memory
            },
        )

    # Create the main agent with subagents
    agent = create_deep_agent(
        backend=backend_factory,
        store=store,
        skills=["/project-docs/", "/coding-standards/"],
        subagents=[
            {
                "name": "researcher",
                "description": "Research papers and documentation",
                "system_prompt": "Find relevant papers and summarize findings",
                "tools": [search_papers, analyze_data],
            },
            {
                "name": "deployer",
                "description": "Deploy services to production after approval",
                "system_prompt": "Deploy services safely, always get approval first",
                "tools": [run_tests, deploy_to_prod],
                "interrupt_on": {"deploy_to_prod": True},
            },
        ],
    )

    return agent


def save_user_preferences(agent, user_id: str, preferences: dict):
    """Save user preferences for cross-session persistence."""
    config = {"configurable": {"thread_id": f"user-{user_id}"}}

    # Try to save preferences to persistent storage
    agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"Save these preferences to /memory/cache/prefs-{user_id}.json: {preferences}",
                }
            ]
        },
        config=config,
    )


def load_user_preferences(agent, user_id: str):
    """Load user preferences from persistent storage."""
    config = {"configurable": {"thread_id": f"user-{user_id}"}}

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"Read preferences from /memory/cache/prefs-{user_id}.json",
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


if __name__ == "__main__":
    print("=" * 60)
    print("Multi-Agent System Demo")
    print("=" * 60)

    print("\n--- Creating agent system ---")
    try:
        agent = create_agent_system()
        print("Agent created successfully")

        # Test 1: Save preferences
        print("\n--- Test 1: Save preferences ---")
        save_user_preferences(agent, "alice", {"theme": "dark", "language": "en"})
        print("Preferences saved")

        # Test 2: Load preferences (after simulated restart)
        print("\n--- Test 2: Load preferences (new session) ---")
        agent2 = create_agent_system()  # Simulate restart
        prefs = load_user_preferences(agent2, "alice")
        print(f"Loaded preferences: {prefs}")

        # Test 3: Research task
        print("\n--- Test 3: Research task ---")
        research = research_topic(agent, "transformer architectures")
        print(f"Research result: {research}")

        # Test 4: Deploy task (should require approval)
        print("\n--- Test 4: Deploy task ---")
        try:
            deploy = deploy_service(agent, "payment-api")
            print(f"Deploy result: {deploy}")
        except Exception as e:
            print(f"Deploy error: {e}")

    except Exception as e:
        print(f"Agent creation failed (expected without API keys): {e}")

    print("\n" + "=" * 60)
