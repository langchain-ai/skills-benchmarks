| Mode | Use When | Returns |
|------|----------|---------|
| `"values"` | Need full state after each step | Complete state dict/object |
| `"updates"` | Need only what changed | State deltas |
| `"messages"` | Need LLM token stream | (token, metadata) tuples / [token, metadata] arrays |
| `"custom"` | Need custom progress signals | User-defined data |
| Multiple modes | Need combined data | List/array of modes |
