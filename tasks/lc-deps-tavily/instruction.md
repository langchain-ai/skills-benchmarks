The project in the current directory has a broken LangChain agent that uses incorrect package dependencies and import paths.

Your job is to fix it so it works correctly.

The problems:
1. requirements.txt uses wrong/outdated package names for Tavily web search
2. The agent code uses incorrect import paths that don't match the installed packages
3. The agent is supposed to do a Tavily web search and return results

Fix the dependency configuration and import paths, then run the agent to confirm it works.

Save the fixed agent to fixed_agent.py and run it with the test query: "What is LangChain?"

IMPORTANT: Run files directly (not in background). If code fails after 2 attempts to fix, save the file and report the error - do not enter debug loops.
