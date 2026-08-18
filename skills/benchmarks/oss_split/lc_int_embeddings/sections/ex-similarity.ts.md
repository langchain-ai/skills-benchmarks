Compute cosine similarity between embeddings.

```typescript
import { OpenAIEmbeddings } from "@langchain/openai";

const embeddings = new OpenAIEmbeddings();

// Embed query and documents
const query = "What is machine learning?";
const docs = [
  "Machine learning is a branch of AI",
  "Paris is the capital of France",
  "Neural networks are used in deep learning",
];

const queryVec = await embeddings.embedQuery(query);
const docVecs = await embeddings.embedDocuments(docs);

// Compute cosine similarity
function cosineSimilarity(vecA: number[], vecB: number[]): number {
  const dotProduct = vecA.reduce((sum, a, i) => sum + a * vecB[i], 0);
  const magnitudeA = Math.sqrt(vecA.reduce((sum, a) => sum + a * a, 0));
  const magnitudeB = Math.sqrt(vecB.reduce((sum, b) => sum + b * b, 0));
  return dotProduct / (magnitudeA * magnitudeB);
}

// Find most similar document
const similarities = docVecs.map((docVec) =>
  cosineSimilarity(queryVec, docVec)
);
console.log("Similarities:", similarities);
const mostSimilarIdx = similarities.indexOf(Math.max(...similarities));
console.log("Most similar doc:", docs[mostSimilarIdx]);
```
