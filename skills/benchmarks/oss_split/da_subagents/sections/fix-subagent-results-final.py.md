Provide complete instructions upfront:

```python
# Subagents return a single final message
# They can't have back-and-forth dialogue with main agent

# Can't do this:
# Main: "task(agent='research', instruction='Find data')"
# Research: "What topic?"
# Main: "AI"
# Research: "Here's AI data"

# Provide complete instructions upfront
# Main: "task(agent='research', instruction='Find data on AI, save to /research/, return summary')"
```
