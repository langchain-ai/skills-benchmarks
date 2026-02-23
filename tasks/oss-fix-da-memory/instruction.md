# Fix: Multi-Agent System Issues

We have a multi-agent system in `environment/agent_system.py` built with deepagents. Users are reporting multiple problems:

- "My preferences are lost when I restart the app"
- "Some files persist but others don't, seems random"
- "The research subagent doesn't have access to our documentation skills"
- "The deployment approval feature doesn't work - it deploys without asking"

## Your Task

Review the agent configuration and fix all issues. Run `python agent_system.py` to see diagnostic output about some of the problems.

After your fixes:
1. User preferences should persist across app restarts
2. Subagents should have access to the same skills/knowledge as the main agent
3. Deployments should pause and require human approval before proceeding
