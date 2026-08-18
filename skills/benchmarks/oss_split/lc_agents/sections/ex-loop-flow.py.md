Agent loop handles multi-step tasks:

```python
agent = create_agent(model="gpt-4.1", tools=[search, get_weather])

# This single invoke() handles the entire loop
result = agent.invoke({
    "messages": [{"role": "user", "content": "Search for the capital of France, then get its weather"}]
})
# Agent automatically calls search → gets "Paris" → calls weather → responds
```
