# Fix: Multi-Agent System Issues

Users are reporting multiple problems with the agent system in `environment/agent_system.py`:

1. **"Preferences don't survive restart"** - User preferences saved in one session are gone when the app restarts, even though they're being saved to what looks like a persistent path.

2. **"Research subagent is useless"** - When asking the researcher to look up documentation, it seems to have no knowledge of project documentation or coding standards that the main agent knows about.

3. **"Deployment happens without approval"** - The deployer subagent is supposed to ask for approval before deploying, but it just deploys immediately without any human confirmation step.

Please investigate and fix all the issues so that:
- User preferences persist across app restarts
- The research subagent has access to the same knowledge as the main agent
- Deployments require explicit approval before proceeding
