Build 4 small components. For each one, choose the right framework and save to the specified file.

1. **Simple Q&A agent** - A basic react agent that answers questions using a search tool. Save to `qa_agent.py`.

2. **Approval pipeline** - A workflow where a draft is generated, then deterministically routed to either an approval step or a revision step based on a quality check. The routing must be explicit and reproducible. Save to `approval_pipeline.py`.

3. **Request middleware** - Add pre/post hooks around an agent: log the input before the agent runs, then log the output after. Save to `middleware_agent.py`.

4. **Research assistant** - An open-ended agent that breaks a research question into sub-tasks and delegates to specialized sub-agents. Save to `research_assistant.py`.

5. **Personal assistant** - An agent with built-in planning and long-term memory management that remembers user preferences and past interactions across sessions. Save to `personal_assistant.py`.

For each component, run a basic test to confirm it works.

IMPORTANT: Run files directly (not in background). If code fails after 2 attempts to fix, save the file and report the error - do not enter debug loops.
