Create new stream each time:

```python
# Problem: Re-using exhausted generator
stream = agent.stream(input)
for mode, chunk in stream:
    print(chunk)

for mode, chunk in stream:  # Empty! Generator exhausted
    print(chunk)

# Solution: Create new stream each time
for mode, chunk in agent.stream(input):
    print(chunk)

# Later...
for mode, chunk in agent.stream(input):  # New stream
    print(chunk)
```
