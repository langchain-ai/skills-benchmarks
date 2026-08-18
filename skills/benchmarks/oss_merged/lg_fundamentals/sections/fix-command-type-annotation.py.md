Command return type needs Literal for routing destinations.
```python
# WRONG
def node_a(state) -> Command:
    return Command(goto="node_b")

# CORRECT
def node_a(state) -> Command[Literal["node_b", "node_c"]]:
    return Command(goto="node_b")
```
