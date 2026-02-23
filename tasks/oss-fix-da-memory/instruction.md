# Fix: Multi-Agent System Issues

We have a multi-agent system in `environment/agent_system.py` built with deepagents. Users are reporting multiple problems:

## Issue 1: Preferences don't persist

```python
# Session 1
agent = create_agent_system()
save_user_preferences(agent, "alice", prefs)
# Saves to: /memory/cache/prefs-alice.json

# Session 2 (restart the app)
agent2 = create_agent_system()
load_user_preferences(agent2, "alice")
# Expected: Returns the saved preferences
# Actual: "No preferences found" - data was lost!
```

Note: The backend routes `/memory/` to persistent storage and `/memory/cache/` to temporary storage.

## Issue 2: Subagent can't access docs

The main agent has `skills=["/project-docs/", "/coding-standards/"]`. But:

```python
research_topic(agent, "info from project-docs")
# Expected: Researcher subagent accesses /project-docs/ and returns info
# Actual: "I don't have access to project documentation"
```

## Issue 3: Deployment skips approval

The deployer subagent has `interrupt_on` configured for `deploy_to_prod` but:

```python
deploy_service(agent, "payment-api")
# Expected: Pauses for human approval before calling deploy_to_prod
# Actual: "Deployed payment-api to production" - no approval requested!
```

## Your Task

Fix all the issues. We've identified in previous testing that the tool implementations (`search_papers`, `deploy_to_prod`, etc.) work as intended - the bugs are in the agent configuration in `create_agent_system()`.

After your fixes:
1. User preferences should persist across app restarts (data saved in one session should be loadable in a new session)
2. Subagents should have access to the same skills/knowledge as the main agent
3. The deployer should pause for human approval before executing `deploy_to_prod`
