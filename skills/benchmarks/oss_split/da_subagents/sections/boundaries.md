**What Agents CAN Configure:**
- Subagent name and description
- Custom tools for subagents
- Different models per subagent
- Subagent-specific system prompts
- Subagent middleware and skills
- Human-in-the-loop for subagent tools

**What Agents CANNOT Configure:**
- Change the `task` tool name
- Make subagents stateful (they're ephemeral)
- Share state directly between subagents
- Remove the default general-purpose subagent
- Have subagents call back to main agent
