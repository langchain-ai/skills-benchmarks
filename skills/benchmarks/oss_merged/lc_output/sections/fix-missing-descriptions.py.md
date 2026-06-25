Add field descriptions to guide the model on expected formats.
```python
# WRONG: No descriptions
class Data(BaseModel):
    date: str
    amount: float

# CORRECT
class Data(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    amount: float = Field(description="Amount in USD")
```
