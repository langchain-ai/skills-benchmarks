# Fix: Multi-Agent System Issues

We have a multi-agent system in `agent_system.py` built with deepagents. Users are reporting several problems — the tool implementations are fine, the issues are in how the agent system is configured.

You may want to reference deepagents documentation on memory backends, subagent configuration, and agent lifecycle management.

## Bug Reports

**1. "My preferences disappear after restarting the app"**

Users save preferences but after restarting, the data is gone. It seems like it's being saved somewhere but not persisting across sessions.

**2. "The research subagent can't access our documentation"**

The main agent can access project docs and coding standards, but when the researcher subagent tries, it says it doesn't have access.

**3. "Deployments go through without approval"**

Production deployments are supposed to require human approval, but they go through immediately without pausing.

## Expected Behavior

1. Preferences saved in one session should be loadable in a new session
2. The researcher subagent should be able to access the main agent's documentation skills
3. The deployer should pause and request approval before executing production deployments
