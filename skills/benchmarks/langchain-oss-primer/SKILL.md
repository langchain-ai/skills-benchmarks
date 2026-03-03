---
name: LangChain OSS Primer
description: "ALWAYS START HERE for any LangChain, Deep Agents, or LangGraph agent building project. Required starting point before choosing other skills or writing any code. Covers framework selection (LangChain vs LangGraph vs Deep Agents), agent archetypes, dependency setup, and which skills to load next based on your decisions."
---

<overview>
**Always load this skill first.** This is the required starting point for any LangChain open source agent project — before choosing other skills, before writing code, before installing packages.

It answers three questions every project must resolve upfront:

1. **Which framework?** — LangChain, LangGraph, or Deep Agents
2. **Which agent archetype?** — maps your use case to the right API and patterns
3. **What to install and which skills to load next**

> Load this skill first. Once you've decided on a framework and agent type, follow the "Next Skills" section at the bottom — it tells you exactly which skills to invoke next based on your choices.
</overview>

---

## Step 1 — Pick Your Framework

The three frameworks are **layered**, not competing. Each builds on the one below:

```
┌─────────────────────────────────────────┐
│              Deep Agents                │  ← batteries included
│   (planning, memory, skills, files)     │
├─────────────────────────────────────────┤
│               LangGraph                 │  ← custom orchestration
│    (nodes, edges, state, persistence)   │
├─────────────────────────────────────────┤
│               LangChain                 │  ← foundation
│      (models, tools, prompts, RAG)      │
└─────────────────────────────────────────┘
```

<framework-decision>

Answer these questions in order:

| Question | Yes → | No → |
|----------|-------|-------|
| User needs or wants planning, persistent memory, complex task management, long-running tasks, out-of-the-box file management, on-demand skills, or built-in middleware, subagents, easy expansion capabilities? | **Deep Agents** | ↓ |
| Needs custom control flow — specified loops, branching, deterministic parallel workers, or manually instrumented human-in-the-loop? | **LangGraph** | ↓ |
| Single-purpose agent with a fixed set of tools? | **LangChain** (`create_agent`) | ↓ |
| Simple prompt pipeline or retrieval chain with no agent loop? | **LangChain** (direct model / chain) | — |

Higher layers depend on lower ones only when necessary — you can mix them. A LangGraph graph can be a subagent inside Deep Agents; LangChain tools work inside both.

</framework-decision>

<framework-profiles>

| | LangChain | LangGraph | Deep Agents |
|---|-----------|-----------|-------------|
| **Control flow** | Fixed (tool loop) | Custom (graph) | Managed (middleware) |
| **Middleware** | Callbacks only | ✗ None | ✓ Explicit, configurable |
| **Planning** | ✗ | Manual | ✓ TodoListMiddleware |
| **File management** | ✗ | Manual | ✓ FilesystemMiddleware |
| **Persistent memory** | ✗ | With checkpointer | ✓ MemoryMiddleware |
| **Subagent delegation** | ✗ | Manual | ✓ SubAgentMiddleware |
| **On-demand skills** | ✗ | ✗ | ✓ SkillsMiddleware |
| **Human-in-the-loop** | ✗ | Manual interrupt | ✓ HumanInTheLoopMiddleware |
| **Custom graph edges** | ✗ | ✓ Full control | Limited |
| **Setup complexity** | Low | Medium | Low |

> **Middleware is a concept specific to Deep Agents (explicit middleware layer). LangGraph has no middleware — behavior is wired directly into nodes and edges. If a user asks for built-in hooks or automatic middleware, route to Deep Agents.**

</framework-profiles>

---

## Step 2 — Pick Your Agent Archetype

Once you've chosen a framework, match your use case to the right API and pattern.

<langchain-archetypes>

### LangChain — use `create_agent()`

Best for single-purpose agents in a ReACT style with a fixed tool set. No built-in planning, memory management, or delegation.

| Archetype | Description | Key tools |
|-----------|-------------|-----------|
| **QA / Chatbot** | Answer questions, summarise, classify. One job, done well. | LLM + optional retrieval |
| **SQL Agent** | Query a database, return structured results | `SQLDatabase`, `create_agent` |
| **Search Agent** | Look up information, return findings | `TavilySearchResults`, `DuckDuckGoSearch` |
| **RAG Agent** | Retrieve from a vector store, ground answers in documents | retriever tool + `create_agent` |
| **Data Analysis Agent** | Load, transform, and summarise structured data | `PythonREPL`, pandas tools |
| **Tool-calling Agent** | Call APIs, run code, or chain arbitrary tools | custom `@tool` functions |

All LangChain agents use `create_agent(model, tools=[...])`. Next skill: **`langchain-fundamentals`**.

</langchain-archetypes>

<langgraph-archetypes>

### LangGraph — use `StateGraph`

Best when you need explicit, deterministic control flow. 

| Archetype | Description | Key pattern |
|-----------|-------------|-------------|
| **Deterministic Parallel Workflows** | Fan out to multiple nodes, collect results, merge | parallel edges → aggregation node | not offloaded to agent decisionmaking
| **Multi-stage Pipeline** | Extract → Transform → Load with typed state | `TypedDict` state + sequential nodes |
| **Branching Classifier** | Route inputs to different handlers based on content | conditional edges + classifer node |
| **Reflection Loop** | Generate → Critique → Revise cycle with explicit exit | cycle edges + iteration counter |
| **Custom HITL** | Complex human-in-the-loop with structured review and conditional edges | `interrupt_before`/`interrupt_after` + `Command` resume |

LangGraph agents use `StateGraph(State)` with explicit `add_node`, `add_edge`, `add_conditional_edges`. Next skill: **`langgraph-fundamentals`**.

</langgraph-archetypes>

<deep-agents-archetypes>

### Deep Agents — use `create_deep_agent()`

Best when the agent needs to manage its own work: planning tasks, remembering users across sessions, delegating to specialists, or managing files autonomously.

| Archetype | Description | Why Deep Agents |
|-----------|-------------|-----------------|
| **Research Assistant** | Receives an open-ended research brief, breaks it into subtasks, delegates to specialist subagents, writes up findings | Needs SubAgentMiddleware for delegation + TodoListMiddleware for planning |
| **Personal Assistant** | Remembers user preferences, ongoing projects, and context across multiple sessions | Needs MemoryMiddleware (Store) for cross-session persistence |
| **Coding Assistant** | Reads codebases, writes files, plans refactors across many steps, optionally asks for approval before writes | Needs FilesystemMiddleware + TodoListMiddleware + optional HITL |
| **Orchestrator** | Top-level agent that routes work to 2+ specialized subagents (researcher, coder, writer…) | Needs SubAgentMiddleware with custom subagent configs |
| **Long-running Task Agent** | Multi-hour or multi-day workflows where state must survive restarts | Needs checkpointer + MemoryMiddleware |
| **On-demand Skills Agent** | Agent that loads different skill sets depending on what the user asks | Needs SkillsMiddleware + FilesystemBackend |
| **Multi Agent Architecture** | Agent that spawns or has access to subagents for isolated tasks |

All Deep Agents use `create_deep_agent(model, tools=[...], ...)`. **Next skill: `deep-agents-core` — load it immediately after deciding on Deep Agents.**

<deep-agents-middleware>

#### Deep Agents built-in middleware

Six components pre-wired out of the box. First three are always active; the rest are opt-in:

| Middleware | Always on? | What it gives the agent |
|------------|-----------|--------------------------|
| `TodoListMiddleware` | ✓ | `write_todos` tool — tracks multi-step task plans |
| `FilesystemMiddleware` | ✓ | `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` |
| `SubAgentMiddleware` | ✓ | `task` tool — delegates subtasks to named subagents |
| `SkillsMiddleware` | Opt-in | Loads SKILL.md files on demand from a skills directory |
| `MemoryMiddleware` | Opt-in | Long-term memory across sessions via a `Store` instance |
| `HumanInTheLoopMiddleware` | Opt-in | Pauses execution and requests human approval before specified tool calls |

You configure middleware — you don't implement it.

</deep-agents-middleware>

<mixing-note>
You can combine layers in the same project. The most common pattern: Deep Agents as the top-level orchestrator, with a compiled LangGraph graph registered as a specialized subagent. LangChain tools and chains are usable at every level.
</mixing-note>

</deep-agents-archetypes>

---

## Step 3 — Set Up Your Dependencies

### Environment requirements

| | Python | TypeScript / Node |
|---|--------|-------------------|
| Runtime | **Python 3.10+** | **Node.js 20+** |
| LangChain | 1.0+ (LTS) | 1.0+ (LTS) |
| LangSmith SDK | >= 0.3.0 | >= 0.3.0 |

> **Always use LangChain 1.0+.** LangChain 0.3 is maintenance-only until December 2026 — do not start new projects on it.

---

### Core packages — always required

<python-core>
**Python**

| Package | Role | Version |
|---------|------|---------|
| `langchain` | Agents, chains, retrieval | `>=1.0,<2.0` |
| `langchain-core` | Base types & interfaces | `>=1.0,<2.0` |
| `langsmith` | Tracing, evaluation, datasets | `>=0.3.0` |
</python-core>

<typescript-core>
**TypeScript**

| Package | Role | Version |
|---------|------|---------|
| `@langchain/core` | Base types & interfaces (peer dep — install explicitly) | `^1.0.0` |
| `langchain` | Agents, chains, retrieval | `^1.0.0` |
| `langsmith` | Tracing, evaluation, datasets | `^0.3.0` |
</typescript-core>

---

### Orchestration — add based on your framework choice

<orchestration-packages>

| Framework | Python | TypeScript |
|-----------|--------|------------|
| LangGraph | `langgraph>=1.0,<2.0` | `@langchain/langgraph ^1.0.0` |
| Deep Agents | `deepagents` (depends on LangGraph; installs it as a transitive dep) | `deepagents` |

</orchestration-packages>

---

### Model providers — pick the one(s) you use

<provider-packages>

| Provider | Python | TypeScript |
|----------|--------|------------|
| OpenAI | `langchain-openai` | `@langchain/openai` |
| Anthropic | `langchain-anthropic` | `@langchain/anthropic` |
| Google Gemini | `langchain-google-genai` | `@langchain/google-genai` |
| Mistral | `langchain-mistralai` | `@langchain/mistralai` |
| Groq | `langchain-groq` | `@langchain/groq` |
| Cohere | `langchain-cohere` | `@langchain/cohere` |
| AWS Bedrock | `langchain-aws` | `@langchain/aws` |
| Azure AI | `langchain-azure-ai` | `@langchain/azure-openai` |
| Ollama (local) | `langchain-ollama` | `@langchain/ollama` |
| Hugging Face | `langchain-huggingface` | — |
| Fireworks AI | `langchain-fireworks` | — |
| Together AI | `langchain-together` | — |

</provider-packages>

---

### Common tools & retrieval — add as needed

<tool-packages>

| Package | Adds | Notes |
|---------|------|-------|
| `langchain-tavily` / `@langchain/tavily` | Tavily web search | Keep at latest; frequently updated for compatibility |
| `langchain-text-splitters` | Text chunking | Semver; keep current |
| `langchain-chroma` / `@langchain/community` | Chroma vector store | Dedicated integration package; keep at latest |
| `langchain-pinecone` / `@langchain/pinecone` | Pinecone vector store | Dedicated integration package; keep at latest |
| `langchain-qdrant` / `@langchain/qdrant` | Qdrant vector store | Dedicated integration package; keep at latest |
| `faiss-cpu` | FAISS vector store (Python only, local) | Via `langchain-community` |
| `langchain-community` / `@langchain/community` | 1000+ integrations fallback | **Python: NOT semver — pin to minor series** |
| `langsmith[pytest]` | pytest plugin | Requires `langsmith>=0.3.4` |

> Prefer dedicated integration packages over `langchain-community` when one exists — they are independently versioned and more stable.

</tool-packages>

---

### Dependency templates

<ex-langchain-python>
<python>
LangChain agent — provider-agnostic starting point.
```
# requirements.txt
langchain>=1.0,<2.0
langchain-core>=1.0,<2.0
langsmith>=0.3.0

# Add your model provider:
# langchain-openai | langchain-anthropic | langchain-google-genai | ...

# Add tools/retrieval as needed:
# langchain-tavily | langchain-chroma | langchain-text-splitters | ...
```
</python>
</ex-langchain-python>

<ex-langgraph-python>
<python>
LangGraph project — provider-agnostic starting point.
```
# requirements.txt
langchain>=1.0,<2.0
langchain-core>=1.0,<2.0
langgraph>=1.0,<2.0
langsmith>=0.3.0

# Add your model provider:
# langchain-openai | langchain-anthropic | langchain-google-genai | ...
```
</python>
</ex-langgraph-python>

<ex-langgraph-typescript>
<typescript>
LangGraph project — provider-agnostic starting point.
```json
{
  "dependencies": {
    "@langchain/core": "^1.0.0",
    "langchain": "^1.0.0",
    "@langchain/langgraph": "^1.0.0",
    "langsmith": "^0.3.0"
  }
}
```
</typescript>
</ex-langgraph-typescript>

<ex-deepagents-python>
<python>
Deep Agents project — provider-agnostic starting point.
```
# requirements.txt
deepagents
langchain>=1.0,<2.0
langchain-core>=1.0,<2.0
langsmith>=0.3.0

# Add your model provider:
# langchain-openai | langchain-anthropic | langchain-google-genai | ...
```
</python>
</ex-deepagents-python>

<ex-deepagents-typescript>
<typescript>
Deep Agents project — provider-agnostic starting point.
```json
{
  "dependencies": {
    "deepagents": "latest",
    "@langchain/core": "^1.0.0",
    "langchain": "^1.0.0",
    "langsmith": "^0.3.0"
  }
}
```
</typescript>
</ex-deepagents-typescript>

---

## Step 4 — Set Your Environment Variables

<environment-variables>
```bash
# LangSmith — always recommended for observability
LANGSMITH_API_KEY=<your-key>
LANGSMITH_PROJECT=<project-name>    # optional, defaults to "default"

# Model provider — set the one(s) you use
OPENAI_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>
GOOGLE_API_KEY=<your-key>
MISTRAL_API_KEY=<your-key>
GROQ_API_KEY=<your-key>
COHERE_API_KEY=<your-key>
FIREWORKS_API_KEY=<your-key>
TOGETHER_API_KEY=<your-key>
HUGGINGFACEHUB_API_TOKEN=<your-key>

# Common tool/retrieval services
TAVILY_API_KEY=<your-key>
PINECONE_API_KEY=<your-key>
```
</environment-variables>

---

## Step 5 — Load the Right Skill Next

Based on the framework and archetype you chose above, invoke these skills **now** before writing any code:

<next-skills>

### If you chose LangChain

| Your archetype | Load next |
|----------------|-----------|
| Any LangChain agent (QA bot, SQL, search, RAG, tool-calling) | **`langchain-fundamentals`** — always |
| Adding external tools/packages (Tavily, Pinecone, etc.) | **`langchain-dependencies`** — package patterns and version guidance |
| Need streaming or async responses | **`langchain-fundamentals`** then `langgraph-fundamentals` |

### If you chose LangGraph

| Your archetype | Load next |
|----------------|-----------|
| Any LangGraph graph | **`langgraph-fundamentals`** — always |
| Approval pipeline, HITL, or pause/resume | **`langgraph-fundamentals`** + `langgraph-human-in-the-loop` |
| State that must survive restarts or cross-thread memory | **`langgraph-persistence`** |
| Streaming output token by token | **`langgraph-fundamentals`** |

### If you chose Deep Agents

**Always load `deep-agents-core` first — it is the mandatory starting point for any Deep Agents project.**

| Your archetype | Load next (after `deep-agents-core`) |
|----------------|--------------------------------------|
| Research Assistant — delegates to specialist subagents | **`deep-agents-orchestration`** — subagent config, TodoList, HITL |
| Personal Assistant — remembers users across sessions | **`deep-agents-memory`** — MemoryMiddleware, Store backends |
| Coding Assistant — reads/writes files, plans refactors | `deep-agents-core` is sufficient; add `deep-agents-orchestration` if using HITL |
| Orchestrator — routes work across multiple named subagents | **`deep-agents-orchestration`** — SubAgentMiddleware patterns |
| Long-running task agent — survives restarts | **`deep-agents-memory`** + `deep-agents-orchestration` |
| On-demand skills agent | `deep-agents-core` covers SkillsMiddleware setup |
</next-skills>
