Write clear, specific tool descriptions.

```python
# Poor description
@tool
def tool1(x: int) -> int:
    """A tool"""  # Too vague!
    return x * 2

# Clear, specific description
@tool
def double_number(number: int) -> int:
    """Multiply a number by 2. Use this when the user wants to double a value.

    Args:
        number: The number to double
    """
    return number * 2
```
