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


def test_persistence():
    """Test that preferences persist across sessions.

    BUG: Data saved to /memory/cache/ is LOST on restart!

    The CompositeBackend routes look correct at first glance:
        /memory/       -> StoreBackend (persistent)
        /memory/cache/ -> StateBackend (ephemeral)

    But CompositeBackend uses LONGEST-PREFIX matching, so when we save
    to /memory/cache/prefs-alice.json, it matches /memory/cache/ (longer)
    instead of /memory/ (shorter), making it ephemeral.

    Example failing interaction:
        Session 1: Save preferences to /memory/cache/prefs-alice.json
        Session 2: Load preferences -> NOT FOUND (data was lost)

    Returns True if persistence works, False otherwise.
    """
    import re

    with open(__file__) as f:
        source = f.read()

    # Check what path is used for preferences
    pref_path_match = re.search(r"/memory/cache/prefs", source)
    if not pref_path_match:
        print("PASS: Not using /memory/cache/ for preferences")
        return True

    # Check if /memory/cache/ routes to StateBackend (ephemeral)
    routes_match = re.search(r"routes\s*=\s*\{([^}]+)\}", source, re.DOTALL)
    if routes_match:
        routes_content = routes_match.group(1)
        # Check if /memory/cache/ uses StateBackend
        if "/memory/cache/" in routes_content and "StateBackend" in routes_content:
            # Check the order - is StateBackend associated with cache?
            cache_state = re.search(r"/memory/cache/.*StateBackend", routes_content, re.DOTALL)
            if cache_state:
                print("FAIL: Preferences are not persisting across restarts")
                return False

    print("PASS: Persistence configuration looks correct")
    return True


def test_subagent_skills_inheritance():
    """Test that subagents have skills configured.

    BUG: Custom subagents DON'T inherit main agent's skills.

    The main agent has skills=["/project-docs/", "/coding-standards/"]
    which gives it access to project-docs/api-reference.md containing
    the API key "PROJ-SK-7X9M2K".

    However, when asking the researcher subagent to look up this key,
    it fails because it doesn't have access to /project-docs/.

    Example failing interaction:
        User: "Use the researcher to find our API secret key"
        Researcher: "I don't have access to project documentation"

    FIX: Add "skills" key to each subagent dict to give them access.

    Returns True if subagents have skills, False otherwise.
    """
    import os
    import re

    # Verify the skill file exists
    skill_file = os.path.join(os.path.dirname(__file__), "project-docs", "api-reference.md")
    if not os.path.exists(skill_file):
        print("SKIP: Skill file not found")
        return True

    # Read this file and check the create_deep_agent call
    with open(__file__) as f:
        source = f.read()

    # Find the main agent's skills
    main_skills_match = re.search(r"skills=\[([^\]]+)\]", source)
    if not main_skills_match:
        print("SKIP: No main agent skills configured")
        return True

    # Find subagents section
    subagent_start = source.find("subagents=[")
    if subagent_start == -1:
        print("SKIP: No subagents configured")
        return True

    subagents_section = source[subagent_start : subagent_start + 2000]

    # Count subagent names
    subagent_names = re.findall(r'"name":\s*"([^"]+)"', subagents_section)

    # Check each subagent for skills
    missing_skills = []
    for name in subagent_names:
        # Find this subagent's block and check for skills
        pattern = rf'"name":\s*"{name}"[^}}]*'
        match = re.search(pattern, subagents_section)
        if match:
            subagent_block = match.group(0)
            if '"skills"' not in subagent_block:
                missing_skills.append(name)

    if missing_skills:
        print(f"\nFAIL: Subagents can't access documentation ({', '.join(missing_skills)})")
        return False

    print("PASS: All subagents have skills configured")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Multi-Agent System Tests")
    print("=" * 60)

    # Test persistence (doesn't require API keys)
    print("\n--- Test: Preference Persistence ---")
    persistence_ok = test_persistence()

    # Test subagent skills (doesn't require API keys)
    print("\n--- Test: Subagent Skills Inheritance ---")
    skills_ok = test_subagent_skills_inheritance()

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
    print("Summary:")
    print("  Persistence test:", "PASSED" if persistence_ok else "FAILED")
    print("  Skills inheritance test:", "PASSED" if skills_ok else "FAILED")
    all_passed = persistence_ok and skills_ok
    print("=" * 60)
    if not all_passed:
        exit(1)
