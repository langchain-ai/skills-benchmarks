Handle context length limits:

```python
# Problem: Input + output exceeds model limit
long_text = "..." * 50000  # Very long text
model = init_chat_model("gpt-4.1")  # 128k context
model.invoke(long_text)  # May succeed

model2 = init_chat_model("gpt-4.1-mini")  # 16k context
model2.invoke(long_text)  # Error: context too long

# Solution: Check input length or use larger context model
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4.1")
tokens = enc.encode(long_text)
print(f"Input tokens: {len(tokens)}")

if len(tokens) > 100000:
    # Use Claude with 200k context
    model = init_chat_model("anthropic:claude-opus-4")
```
