Parallel tool calls in one step:

```python
# Models can call multiple tools simultaneously
agent = create_agent(
    model="gpt-4.1",
    tools=[get_weather, get_news],
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Get weather for NYC and latest news for SF"
    }]
})

# Agent may call both tools in parallel in a single step
```
