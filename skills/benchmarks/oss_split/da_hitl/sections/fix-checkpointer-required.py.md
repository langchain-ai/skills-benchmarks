Provide checkpointer for interrupt state:

```python
# This will error
agent = create_deep_agent(
    interrupt_on={"write_file": True}
)

# Must provide checkpointer
agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)
```
