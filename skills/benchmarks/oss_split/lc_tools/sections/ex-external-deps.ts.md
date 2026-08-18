TypeScript with axios:

```typescript
import axios from "axios";

const githubSearch = tool(
  async ({ query, language }) => {
    const response = await axios.get("https://api.github.com/search/repositories", {
      params: { q: `${query} language:${language}`, sort: "stars" },
      headers: { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` },
    });

    const repos = response.data.items.slice(0, 5);
    return repos.map(r => `${r.full_name} (stars: ${r.stargazers_count})`).join("\n");
  },
  {
    name: "search_github",
    description: "Search GitHub repositories",
    schema: z.object({
      query: z.string().describe("Search query"),
      language: z.string().optional().describe("Programming language filter"),
    }),
  }
);
```
