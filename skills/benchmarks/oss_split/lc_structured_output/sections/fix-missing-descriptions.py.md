Add Field descriptions for clarity.

```python
# Problem: No field descriptions
class Data(BaseModel):
    date: str  # What format?
    amount: float  # What unit?

# Solution: Add descriptions via Field
class Data(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    amount: float = Field(description="Amount in USD")
```
