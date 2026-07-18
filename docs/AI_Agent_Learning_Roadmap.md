# AI Agent Platform Learning Roadmap

> **Project:** AI Agent Platform (CLI)
>
> **Goal:** Learn AI Engineering, LangChain, LangGraph, and Production AI Agent Architecture by building a real-world CLI AI Agent from scratch.
>
> **Learning Style**
>
> - Learn **Architecture First**
> - Then **Implement**
> - Then **Trace Execution**
> - Then **Quiz**
> - Finally **Refactor & Improve**

---

# Overall Learning Roadmap

```text
Foundation
      │
      ▼
Python Async Architecture
      │
      ▼
LLM Architecture
      │
      ▼
CLI Architecture
      │
      ▼
LangGraph Fundamentals
      │
      ▼
Checkpoint Architecture
      │
      ▼
Streaming Architecture
      │
      ▼
Interrupt & Human In The Loop
      │
      ▼
Memory Architecture
      │
      ▼
RAG Architecture
      │
      ▼
Subgraphs
      │
      ▼
Multi-Agent Systems
      │
      ▼
Production AI Platform
```

---

# Phase 1 — Foundation ✅

## Status

✅ Completed

---

## Learned

### Python

- Project Structure
- Modules & Packages
- Dataclasses
- Type Hints
- Enums
- Logging
- Configuration Management
- Environment Variables

---

### Async Python

- async / await
- Event Loop
- Async Functions
- Async Context Managers
- Async Iterators
- Async Generators

---

### Software Architecture

- Dependency Injection
- Repository Pattern
- Service Layer
- Manager Pattern
- Separation of Concerns

---

### CLI

Built

- Rich CLI
- Renderer
- Chat Loop

---

# Phase 2 — LLM Architecture ✅

## Status

✅ Completed

---

## Learned

### LLMManager

- Multi-provider Architecture
- Google
- OpenAI
- Anthropic
- Groq

---

### Model Configuration

- Temperature
- Max Tokens
- Streaming
- Tool Binding

---

### Prompt Flow

```text
User

↓

Messages

↓

LLM

↓

AIMessage
```

---

# Phase 3 — Session Architecture ✅

## Status

✅ Completed

---

## Learned

### SessionManager

- Session Creation
- Session Switching
- Session Metadata
- SQLite Persistence

---

### History

- Conversation History
- BaseMessage
- HumanMessage
- AIMessage

---

# Phase 4 — LangGraph Fundamentals ✅

## Status

✅ Completed

---

## Architecture Learned

### StateGraph

- Graph Builder
- Compiled Graph
- Execution Engine

---

### State

- GraphState
- State Updates
- Shared State

---

### Reducers

- Default Reducer
- add_messages
- Custom Reducers

---

### Nodes

- Chatbot Node
- Plain Python Functions
- State Input
- Partial State Output

---

### Edges

- add_edge()
- add_conditional_edges()

---

### ToolNode

Learned internally

- Tool Registration
- Tool Lookup
- Tool Dispatch
- Parallel Tool Execution
- Error Handling

---

### Tool Binding

Learned

- bind_tools()
- Tool Schema
- AIMessage.tool_calls

---

### Routing

- tools_condition()
- Conditional Routing
- Graph Topology

---

### Command

Learned

- goto
- update
- Dynamic Routing
- Loops
- State Merge

---

### Execution Engine

Learned complete flow

```text
User

↓

State

↓

Node

↓

State Update

↓

Router

↓

Next Node

↓

END
```

---

# Phase 5 — ReAct Agent ✅

## Status

✅ Completed

---

## Learned

```text
HumanMessage

↓

AIMessage(tool_calls)

↓

ToolNode

↓

ToolMessage

↓

AIMessage
```

---

### Built

- Weather Tool
- Search Tool
- News Tool

---

# Phase 6 — Checkpoint Architecture

## Status

🟡 Partially Implemented

❌ Architecture not fully learned

---

## Already Implemented

- AsyncSqliteSaver
- thread_id
- SQLite Checkpointer

---

## Still Need to Learn

### Internal Architecture

- What is a Checkpoint?
- Why Checkpointer exists
- What gets serialized?
- What is NOT serialized?
- thread_id lifecycle
- Graph Resume
- Crash Recovery
- Persistent Execution
- Checkpoint Storage

---

# Phase 7 — Streaming Architecture

## Status

🟡 Partially Implemented

---

## Already Implemented

- graph.astream_events()
- Rich Streaming

---

## Still Need to Learn

### Internal Architecture

- Event System
- Stream Modes
- Event Lifecycle
- Token Events
- Tool Events
- Metadata Events
- Renderer Flow
- Why nodes don't stream directly

---

# Phase 8 — Interrupt & Human In The Loop

## Status

⬜ Not Started

---

## Need to Learn

- interrupt()
- Resume
- Human Approval
- Command(resume)
- Review Loops
- Pause Execution
- Approval Workflow

---

# Phase 9 — Memory Architecture

## Status

⬜ Not Started

---

## Need to Learn

### Short-Term Memory

- Conversation State
- Context Window

---

### Long-Term Memory

- User Memory
- Semantic Memory

---

### Summarization

- Message Compression
- Memory Summaries
- Context Management

---

# Phase 10 — RAG

## Status

⬜ Not Started

---

## Need to Learn

### Embeddings

- Embedding Models
- Dimensions
- Similarity

---

### Vector Database

- Chroma
- FAISS
- PGVector

---

### Retrieval

- Indexing
- Searching
- Ranking
- Context Injection

---

### RAG Flow

```text
Question

↓

Retriever

↓

Documents

↓

Context

↓

LLM
```

---

# Phase 11 — Subgraphs

## Status

⬜ Not Started

---

## Need to Learn

- Subgraphs
- Nested Graphs
- Graph Composition
- Reusable Workflows

---

# Phase 12 — Multi-Agent Systems

## Status

⬜ Not Started

---

## Need to Learn

### Supervisor Pattern

```text
Supervisor

↓

Worker Agent

↓

Reviewer

↓

Supervisor
```

---

### Agent Types

- Planner
- Researcher
- Coder
- Reviewer
- Browser
- SQL Agent

---

### Concepts

- Delegation
- Coordination
- Agent Communication
- Shared State

---

# Phase 13 — Production AI Architecture

## Status

⬜ Not Started

---

## Need to Learn

### Observability

- Logging
- Tracing
- Metrics

---

### Cost Tracking

- Token Usage
- Cost Estimation

---

### Deployment

- Docker
- PostgreSQL
- Redis

---

### Scaling

- Background Workers
- Queues
- Horizontal Scaling

---

### Security

- Secrets
- Rate Limits
- Authentication

---

# Phase 14 — MCP (Model Context Protocol)

## Status

⬜ Not Started

---

## Need to Learn

- MCP Basics
- MCP Server
- MCP Client
- Tool Discovery
- Resources
- Prompts
- Remote Tool Execution

---

# Final Project

After completing every phase, the CLI AI Agent should support:

- Multi-provider LLM
- LangGraph
- Tool Calling
- Streaming
- SQLite Checkpoints
- Session Management
- Memory
- RAG
- Human Approval
- Multi-Agent Workflows
- MCP
- Token Usage
- Cost Tracking
- Rich CLI
- Production Architecture

---

# Progress Tracker

| Phase | Topic | Status |
|---------|------|--------|
| 1 | Foundation | ✅ Completed |
| 2 | LLM Architecture | ✅ Completed |
| 3 | Session Architecture | ✅ Completed |
| 4 | LangGraph Fundamentals | ✅ Completed |
| 5 | ReAct Agent | ✅ Completed |
| 6 | Checkpoint Architecture | 🟡 Implementation Done / Theory Pending |
| 7 | Streaming Architecture | 🟡 Implementation Done / Theory Pending |
| 8 | Human In The Loop | ⬜ |
| 9 | Memory Architecture | ⬜ |
| 10 | RAG | ⬜ |
| 11 | Subgraphs | ⬜ |
| 12 | Multi-Agent Systems | ⬜ |
| 13 | Production AI Architecture | ⬜ |
| 14 | MCP | ⬜ |

---

# Learning Rule

For **every future phase**, follow the same process:

1. **Architecture**
   - Why does it exist?
   - What problem does it solve?
   - How does it work internally?

2. **Implementation**
   - Add it to the CLI AI Agent.

3. **Execution Trace**
   - Follow the request through the code step by step.

4. **Quiz**
   - Verify understanding with practical questions.

5. **Refactor**
   - Improve the implementation based on architectural understanding.

---

# Session Notes

At the end of each learning session, update:

- Current Phase
- Topics Completed
- Architecture Learned
- Code Implemented
- Remaining Tasks
- Questions to Review Next Session

This document becomes the single source of truth for tracking progress and deciding what to learn next.