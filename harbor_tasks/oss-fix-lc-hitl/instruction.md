# Fix: Document Management Agent Approval Workflow

We have a LangChain agent in `broken_agent.py` for managing documents. Users are reporting multiple problems:

- "Dangerous operations like 'delete' execute without any approval step"
- "After I approve an action, the system starts from scratch instead of continuing where it left off"
- "The action history only shows my last action — all previous actions disappeared"
- "I can see other users' action history mixed with mine"

## Current Behavior

```
User: Delete the document 'old_drafts'
Agent: Permanently deleted document 'old_drafts'   <-- Executed without approval!
```

## Expected Behavior

```
User: Delete the document 'old_drafts'
Agent: [paused — waiting for human approval before executing delete_document]

User: [approves]
Agent: Permanently deleted document 'old_drafts'   <-- Resumes and completes
```

## Your Task

Review the agent code and fix all issues causing the approval and state problems. The tools and model are correct — focus on how the agent is created and invoked.

After your fixes:
1. Dangerous tool calls (like delete) should pause for human approval before executing
2. Resuming after approval should continue the interrupted action, not start over
3. State should persist between separate calls
4. Different users should have isolated conversations (not share state)
