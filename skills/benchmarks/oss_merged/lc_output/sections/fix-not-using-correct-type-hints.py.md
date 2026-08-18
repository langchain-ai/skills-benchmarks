Use proper type hints for Pydantic fields for correct schema generation.
```python
# WRONG: Missing type hints
class Data(BaseModel):
    items = []  # No type hint!

# CORRECT
class Data(BaseModel):
    items: List[str] = Field(default_factory=list)
```
