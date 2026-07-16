# LangGraph Learning Progress Summary

> **Project:** AI Agent Platform (CLI)
>
> **Current Milestone:** ✅ Production-style LangGraph ReAct Agent with Tool Calling

---

# Project Goal

The goal of this project is **not just to build an AI chatbot**, but to **learn LangGraph deeply** by implementing every concept from scratch.

The long-term objective is to build a production-ready AI Agent Platform that supports:

- Tool Calling
- Conversation Memory
- Persistent Checkpointing
- RAG
- Streaming
- Multi-Agent Workflows
- Planning & Reasoning
- Human-in-the-loop
- Production Deployment

Every component is built manually to understand **why it exists**, not just how to use it.

---

# Technology Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.13 |
| Agent Framework | LangGraph |
| LLM Framework | LangChain |
| LLM Provider | Google Gemini |
| Database | SQLite |
| ORM | SQLAlchemy Async |
| HTTP Client | HTTPX |
| CLI | Rich |
| Search | Tavily |
| Weather | OpenWeather |

---

# Current Architecture

```text
User
 │
 ▼
CLI
 │
 ▼
ChatService
 │
 ▼
LangGraph
 │
 ▼
Chatbot Node
 │
 ▼
tools_condition
 ├─────────────┐
 │             │
 ▼             ▼
ToolNode      END
 │
 ▼
ToolMessage
 │
 ▼
Chatbot Node
 │
 ▼
Final AIMessage
```

---

# Completed Modules

## ✅ Foundation

Implemented:

- Configuration Management
- Environment Variables
- Logger
- CLI Renderer
- Project Structure

---

## ✅ LLM Manager

Created a dedicated `LLMManager`.

Responsibilities:

- Initialize providers
- Configure models
- Configure temperature
- Configure max tokens
- Support streaming
- Abstract provider differences

Supported Providers:

- Google Gemini
- OpenAI
- Anthropic
- Groq

Available Methods:

```python
invoke()
ainvoke()
stream()
astream()
```

---

## ✅ Session Management

Created:

```
SessionManager
```

Responsibilities:

- Create Session
- Switch Session
- Delete Session
- List Sessions
- Retrieve Current Session

Session metadata includes:

- Session ID
- Title
- Created Time
- Updated Time

Sessions are persisted in SQLite.

---

## ✅ Conversation History

Created:

```
HistoryManager
```

Current implementation:

```python
dict[str, list[BaseMessage]]
```

Messages are currently stored **in memory**.

### Decision

History persistence is intentionally postponed until learning **LangGraph Checkpointers**.

---

## ✅ Database Layer

Implemented:

- SQLAlchemy Async Engine
- AsyncSession
- AsyncSessionLocal
- Base Models
- Repository Pattern

Current Repository:

```
SessionRepository
```

Architecture:

```text
AsyncSession
      │
      ▼
Repository
      │
      ▼
Manager
      │
      ▼
Service
```

---

## ✅ Dependency Injection

Created:

```
core/bootstrap.py
```

Responsibilities:

- Build application dependencies
- Create database session
- Create repositories
- Create managers
- Create services

Factory:

```python
async def create_chat_service()
```

Dependency Flow:

```text
AsyncSession
      │
      ▼
SessionRepository
      │
      ▼
SessionManager
      │
      ▼
HistoryManager
      │
      ▼
ChatService
```

ChatService no longer creates its own dependencies.

---

## ✅ Async Architecture

Entire application converted to Async.

Execution Flow:

```text
asyncio.run(main())

↓

await CLI.run()

↓

await ChatService.get_response()

↓

await ChatService.chat()

↓

await graph.ainvoke()

↓

await chatbot_node()

↓

await llm.ainvoke()
```

---

# LangGraph

---

## ✅ GraphState

Created:

```python
GraphState
```

Contains:

```python
messages
```

Using:

```python
Annotated[
    list[BaseMessage],
    add_messages,
]
```

---

## ✅ Chatbot Node

Created:

```python
create_chatbot_node(
    llm,
    tools,
)
```

Returns:

```python
chatbot_node(state)
```

Responsibilities:

- Receive GraphState
- Bind Tools
- Invoke LLM
- Return updated state

---

### Important Lesson Learned

Never recreate AIMessage.

Wrong:

```python
AIMessage(
    content=response.content,
)
```

Correct:

```python
return {
    "messages": [
        response,
    ]
}
```

Reason:

Creating a new AIMessage removes:

- tool_calls
- metadata
- response ID
- usage metadata

Without tool_calls the graph cannot execute tools.

---

## ✅ GraphBuilder

Created:

```
GraphBuilder
```

Responsibilities:

- Build StateGraph
- Register Nodes
- Register Edges
- Compile Graph

---

Current Graph:

```text
START

↓

Chatbot

↓

tools_condition

↓

ToolNode

↓

Chatbot

↓

END
```

---

## ✅ Routing

Using built-in LangGraph routing:

```python
tools_condition
```

Instead of custom routing.

LangGraph automatically decides:

```text
Tool Needed?

YES
 ↓
ToolNode

NO
 ↓
END
```

---

# Tool Calling

---

## Weather Tool

Implemented:

```python
get_weather()
```

Features:

- OpenWeather API
- Async HTTPX
- Error Handling

---

## Google Search Tool

Implemented.

Current Status:

✅ Working

---

## News Tool

Implemented.

Uses:

- Tavily Search

Needs:

```
TAVILY_API_KEY
```

---

# ChatService

Responsibilities:

- Validate User Input
- Load/Create Session
- Save User Message
- Load Conversation History
- Execute LangGraph
- Save Assistant Message
- Return Final Response

Important:

ChatService no longer talks directly to the LLM.

Everything goes through LangGraph.

---

# ReAct Agent

Successfully implemented LangGraph ReAct workflow.

Verified execution:

```text
HumanMessage

↓

AIMessage
(tool_calls)

↓

ToolNode

↓

ToolMessage

↓

AIMessage
(final answer)
```

This confirms:

- Tool Binding
- Tool Routing
- Tool Execution
- Final Reasoning

are all working correctly.

---

# Major Bugs Solved

## AIMessage Recreation

Problem:

Tool calls disappeared.

Cause:

Creating a new AIMessage.

Solution:

Return original response.

---

## Async Cascade

Converted entire application to async.

Every layer now supports async execution.

---

## SQLite Driver

Changed:

```
sqlite://
```

to

```
sqlite+aiosqlite://
```

---

## Dependency Injection

Removed manual dependency creation.

Introduced Bootstrap Layer.

---

## Repository Bugs

Fixed incorrect model handling.

Corrected SQLAlchemy usage.

---

## SQLite Tables

Added:

```python
await init_database()
```

during application startup.

---

# Current Working Features

| Feature | Status |
|----------|--------|
| CLI | ✅ |
| Async Architecture | ✅ |
| Dependency Injection | ✅ |
| SQLite Sessions | ✅ |
| In-Memory History | ✅ |
| LangGraph | ✅ |
| Tool Calling | ✅ |
| Weather Tool | ✅ |
| Search Tool | ✅ |
| News Tool | ✅ |
| ReAct Agent | ✅ |

---

# Folder Structure

```text
core/
│
├── bootstrap.py
│
├── graph/
│   ├── graph.py
│   ├── nodes.py
│   └── state.py
│
├── llm/
│   └── manager.py
│
├── memory/
│   ├── history.py
│   └── session.py
│
├── database/
│   ├── db.py
│   ├── models/
│   └── repositories/
│
├── tools/
│   ├── weather.py
│   ├── search.py
│   └── news.py
│
services/
│
└── chat_service.py
│
interfaces/
│
└── cli/
```

---

# Learning Achievements

Completed:

- ✅ Python Async
- ✅ SQLAlchemy Async
- ✅ Repository Pattern
- ✅ Dependency Injection
- ✅ LangChain Basics
- ✅ LangGraph Basics
- ✅ StateGraph
- ✅ GraphState
- ✅ Nodes
- ✅ Edges
- ✅ Conditional Routing
- ✅ ToolNode
- ✅ ReAct Pattern
- ✅ Tool Calling

---

# Next Learning Phase

## LangGraph Checkpointers

Topics to Learn:

- What is a Checkpointer?
- Why LangGraph uses Checkpointers
- MemorySaver
- SQLite Checkpointer
- Thread IDs
- Resuming Conversations
- Graph Persistence
- Difference between:
  - SessionManager
  - HistoryManager
  - Checkpointer

---

# Long-Term Roadmap

```text
✅ Foundation

✅ Configuration

✅ Logger

✅ CLI

✅ LLM Manager

✅ Session Management

✅ Conversation History

✅ SQLite

✅ Dependency Injection

✅ LangGraph Basics

✅ ReAct Agent

────────────────────────────

⬜ LangGraph Checkpointers

⬜ Streaming

⬜ Long-Term Memory

⬜ RAG

⬜ Memory Summarization

⬜ Multi-Step Planning

⬜ Multi-Agent Architecture

⬜ Human-in-the-Loop

⬜ Observability

⬜ Production Deployment
```

---

# Current Milestone

🎉 **Milestone Achieved: Production-Style LangGraph ReAct Agent**

The application now supports:

- Modular architecture
- Async execution
- SQLite session persistence
- LangGraph state management
- Automatic tool calling
- Multiple tools
- ReAct reasoning loop
- Clean dependency injection

This serves as the stable foundation for learning advanced LangGraph concepts such as Checkpointers, Streaming, RAG, and Multi-Agent systems.