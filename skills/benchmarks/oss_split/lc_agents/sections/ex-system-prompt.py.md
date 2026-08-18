Agent with custom system prompt:

```python
agent = create_agent(
    model="gpt-4.1",
    tools=[search, calculator],
    system_prompt="""You are a helpful research assistant.
Always cite your sources when using the search tool.
Show your work when performing calculations.""",
)
```
