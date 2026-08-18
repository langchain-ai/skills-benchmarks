Load GitHub repository:

```typescript
import { GithubRepoLoader } from "@langchain/community/document_loaders/web/github";

const loader = new GithubRepoLoader(
  "https://github.com/langchain-ai/langchainjs",
  {
    branch: "main",
    recursive: true,
    ignorePaths: ["node_modules/**", "dist/**"],
    maxConcurrency: 5,
  }
);

const docs = await loader.load();
// Each file becomes a document
```
