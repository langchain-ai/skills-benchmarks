# Fix: Customer Support Bot Memory Issues

We have a LangGraph chatbot in `broken_agent.py` for handling customer inquiries. Users are reporting multiple problems:

- "The bot forgets what I said earlier in the same conversation"
- "Sometimes my messages just disappear"
- "When I come back later, it doesn't remember our previous chat"

## Current Behavior

```
User: Hi! My name is Sarah
Bot: I heard: Hi! My name is Sarah

User: What is my name?
Bot: I don't know your name yet. What is it?   <-- Should remember Sarah!
```

## Expected Behavior

```
User: Hi! My name is Sarah
Bot: I heard: Hi! My name is Sarah

User: What is my name?
Bot: Your name is Sarah!   <-- Remembers the name
```

## Your Task

Review the agent code and fix all issues causing the memory problems. The logic for extracting names and generating responses is correct - the issues are with how state is managed and persisted.

After your fixes:
1. Messages should accumulate in the conversation history (not get overwritten)
2. State should persist between separate `chat()` calls
3. Different users should have isolated conversations (not share state)
