Use correct temperature range:

```python
# Problem: Wrong temperature range
model = ChatOpenAI(
    temperature=10,  # Too high! Should be 0-1
)

# Solution: Use 0-1 range
deterministic = ChatOpenAI(temperature=0)  # Always same
balanced = ChatOpenAI(temperature=0.7)  # Default
creative = ChatOpenAI(temperature=1)  # Maximum randomness
```
