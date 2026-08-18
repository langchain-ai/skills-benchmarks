Add error handling paths:

```python
# ANTI-PATTERN - Overly rigid workflow
# What if validation fails? No recovery path!
.add_edge("validate", "process")  # Always proceeds

# BETTER - Add conditional logic
def route_after_validate(state):
    if not state["validated"]:
        return "error_handler"
    return "process"

.add_conditional_edges("validate", route_after_validate)
```
