Provider-specific class initialization:

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { ChatAnthropic } from "@langchain/anthropic";
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";

// OpenAI
const openai = new ChatOpenAI({
  model: "gpt-4.1",
  temperature: 0.7,
  maxTokens: 1000,
  apiKey: process.env.OPENAI_API_KEY,
});

// Anthropic
const anthropic = new ChatAnthropic({
  model: "claude-sonnet-4-5-20250929",
  temperature: 0,
  maxTokens: 2000,
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Google
const google = new ChatGoogleGenerativeAI({
  model: "gemini-2.5-flash-lite",
  temperature: 0.5,
  apiKey: process.env.GOOGLE_API_KEY,
});
```
