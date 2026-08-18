Use dynamic interrupts instead:

```python
# ANTI-PATTERN - Static breakpoints for all users
compile(interrupt_before=["action"])  # Pauses for everyone!

# BETTER - Dynamic interrupts with logic
def node(state):
    if state["requires_approval"]:  # Conditional
        interrupt({"action": "approve?"})
```
