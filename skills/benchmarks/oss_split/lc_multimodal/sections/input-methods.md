| Method | When to Use | Example |
|--------|-------------|---------|
| URL | Public images | `{ type: "image", url: "https://..." }` |
| Base64 | Private/local images | `{ type: "image", data: "base64..." }` / `{ "type": "image", "base64": "..." }` |
| File reference | Provider file APIs | `{ type: "image", fileId: "..." }` |
