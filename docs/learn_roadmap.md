# 🚀 AI Agent Engineering Roadmap (4 Weeks)

> A practical roadmap to learn **LLMs, RAG, LangChain, LangGraph, MCP, Multi-Agent Systems, and Production AI Engineering** through hands-on projects.

## 📌 Course Overview

- **Duration:** 4 Weeks
- **Study Time:** 4–6 Hours / Day
- **Approach:** 30% Theory • 70% Hands-on
- **Final Goal:** Build production-ready AI agents and enterprise AI applications.

---

# 📅 Weekly Schedule

| Week | Focus | Outcome |
|-------|-------|---------|
| Week 1 | LLM Foundations & AI Agents | Build your first AI Assistant |
| Week 2 | RAG & Agent Capabilities | Build a PDF QA + RAG Agent |
| Week 3 | LangGraph & Multi-Agent Systems | Build a Research Agent |
| Week 4 | Production AI Engineering | Build an Enterprise AI Platform |

---

# Week 1 — Foundations of LLMs & AI Agents

**Presenter:** Ayush & Kishor

**Goal**

Understand how Large Language Models work before using frameworks.

---

## Module 1 — Core AI Concepts

### Topics

- Artificial Intelligence vs Machine Learning vs Deep Learning
- Natural Language Processing (NLP)
- Generative AI
- Transformer Architecture (High Level)
- Encoder vs Decoder Models
- Training vs Inference
- Foundation Models

### Learn

- Why LLMs changed AI
- How transformers process language
- How inference differs from training
- Why scaling laws matter

---

## Module 2 — LLM Fundamentals

### Topics

- Tokenization
- Embeddings
- Context Window
- Positional Encoding
- Attention Mechanism
- Temperature
- Top-K
- Top-P
- Token Cost
- Hallucinations
- Model Limitations

### Missing Topics Added

- System Prompts
- Model Selection (GPT, Claude, Gemini, Open Source)
- Context Management
- Prompt Caching (Overview)

---

## Module 3 — Prompt Engineering

### Topics

- Zero-shot Prompting
- Few-shot Prompting
- Chain of Thought (CoT)
- Role Prompting
- XML Prompting
- JSON Prompting
- Structured Outputs
- Prompt Templates

### Missing Topics Added

- Prompt Versioning
- Prompt Evaluation
- Prompt Optimization
- Prompt Guardrails

---

## Module 4 — AI Agents

### Topics

- What is an AI Agent?
- Agent Lifecycle (Think → Plan → Act → Observe)
- ReAct Framework
- Planning vs Execution
- Tool Calling
- Function Calling

### Missing Topics Added

- Agent Memory Overview
- Agent Personas
- Agent Decision Flow

---

## Hands-on

Build:

- CLI Chatbot
- Weather Assistant
- Search Assistant

### Tech Stack

- OpenAI SDK
- Azure OpenAI (Overview)
- Gemini SDK
- Anthropic SDK

---

## Weekly Presentation

**How Large Language Models Work**

---

## Weekly Project

### AI Assistant

Features

- Streaming Chat
- Conversation History
- Weather Tool
- Search Tool
- Function Calling

---

# Week 2 — Building Agent Capabilities

**Presenter:** Yashika & Jaswantha

**Goal**

Enable AI agents to retrieve knowledge, use tools, and remember conversations.

---

## Module 1 — Embeddings & Retrieval

### Topics

- Embeddings
- Similarity Search
- Cosine Similarity
- Dot Product
- Euclidean Distance

### Missing Topics Added

- Embedding Models
- Embedding Dimensions
- Embedding Optimization

---

## Module 2 — Vector Databases

### Topics

- ChromaDB
- FAISS
- PGVector
- Pinecone (Overview)

### Learn

- Indexing
- Metadata
- Filtering
- Semantic Search

---

## Module 3 — RAG

### Topics

- Retrieval Augmented Generation
- Chunking
- Query Retrieval
- Context Injection

### Missing Topics Added

- Query Rewriting
- Hybrid Search
- Reranking
- Context Compression
- Citation Generation
- Agentic RAG

---

## Module 4 — Memory Systems

### Topics

- Conversation Memory
- Short-term Memory
- Long-term Memory
- Semantic Memory

### Missing Topics Added

- Vector Memory
- Redis Memory
- Memory Compression

---

## Module 5 — Tools & Integrations

### Topics

- REST APIs
- Web Search
- Database Access
- File Operations

### Missing Topics Added

- SQL Tool
- Python REPL Tool
- Email Tool
- Calendar Tool

---

## Module 6 — Frameworks

### LangChain

- Models
- Prompt Templates
- Chains
- LCEL
- Output Parsers
- Tools

### LangGraph

- StateGraph
- Nodes
- Edges
- Conditional Routing

### MCP

- Model Context Protocol
- MCP Server
- MCP Client
- Resources
- Tool Discovery

---

## Hands-on

Build

- PDF Question Answering Agent
- RAG Agent using ChromaDB / FAISS

---

## Weekly Presentation

**Building Production RAG Systems**

---

## Weekly Project

Knowledge Base Assistant

Features

- Upload PDFs
- Ask Questions
- Conversation Memory
- Vector Search
- Source Citations

---

# Week 3 — Agentic Workflows & Multi-Agent Systems

**Presenter:** Sumit Verma & Aditya

**Goal**

Build autonomous workflows with multiple collaborating AI agents.

---

## Module 1 — Agent Design Patterns

### Topics

- ReAct
- Plan-and-Execute
- Reflection
- Self-Correction
- Tree of Thoughts

### Missing Topics Added

- Router Pattern
- Supervisor Pattern
- Critic Pattern
- Reviewer Pattern

---

## Module 2 — Multi-Agent Systems

### Topics

- Supervisor Agent
- Worker Agents
- Agent Communication
- Agent Orchestration

### Learn

- Task Delegation
- Parallel Execution
- Shared Memory

---

## Module 3 — Frameworks

### LangGraph Advanced

- Commands
- Interrupts
- Checkpointing
- Persistence
- Human-in-the-loop

### CrewAI

### AutoGen

### Missing Topics Added

- OpenAI Agents SDK (Overview)
- Workflow Comparison

---

## Module 4 — Evaluation

### Topics

- Agent Benchmarking
- Prompt Evaluation
- Tracing
- Debugging

### Missing Topics Added

- Hallucination Evaluation
- Faithfulness
- Groundedness
- Latency
- Token Cost

---

## Hands-on

Build

- Research Agent
- Multi-Agent Content Generator

Architecture

Planner

↓

Researcher

↓

Writer

↓

Reviewer

↓

Final Response

---

## Weekly Presentation

**Designing Multi-Agent AI Systems**

---

## Weekly Project

Research Assistant

Features

- Multi-Agent Workflow
- Web Search
- Reflection
- Final Review

---

# Week 4 — Production Agent Engineering

**Presenter:** Aditya Jain, Mansi & Asad

**Goal**

Deploy secure, scalable, production-ready AI systems.

---

## Module 1 — Reliability & Safety

### Topics

- Guardrails
- Hallucination Mitigation
- Output Validation
- Human-in-the-loop

### Missing Topics Added

- Prompt Injection Protection
- Jailbreak Prevention
- AI Safety

---

## Module 2 — Observability

### Topics

- LangSmith
- Tracing
- Monitoring
- Cost Tracking

### Missing Topics Added

- OpenTelemetry
- Logging
- Metrics
- Performance Monitoring

---

## Module 3 — Deployment

### Topics

- FastAPI
- Docker
- Cloud Deployment (Azure, AWS, GCP)
- CI/CD

### Missing Topics Added

- Docker Compose
- Redis
- PostgreSQL
- Nginx
- Reverse Proxy

---

## Module 4 — Advanced AI Engineering

### Topics

- Agent Memory Architectures
- Long Context Techniques
- AI Workflows vs Agents
- Agentic RAG

### Missing Topics Added

- Model Routing
- Semantic Caching
- Cost Optimization
- Multi-Tenant AI Systems
- Rate Limiting

---

# 🚀 Final Capstone Project

## Enterprise AI Platform

Build a production-ready AI platform with:

- Authentication
- AI Chat
- LangGraph Workflows
- Multi-Agent System
- RAG Pipeline
- PDF Processing
- Web Search
- MCP Integration
- PostgreSQL
- Redis
- FastAPI
- Docker
- Observability
- Evaluation
- Deployment

---

# 📊 Recommended Learning Order

1. LLM Fundamentals
2. Prompt Engineering
3. Function Calling
4. Embeddings
5. Vector Databases
6. RAG
7. LangChain
8. LangGraph
9. MCP
10. Agent Design Patterns
11. Multi-Agent Systems
12. Evaluation & Observability
13. Production Deployment

---

# ⏰ Daily Study Plan (4–6 Hours)

| Activity | Duration |
|----------|----------|
| Theory & Concepts | 1 Hour |
| Documentation | 30 Minutes |
| Hands-on Coding | 2 Hours |
| Build Project | 1–2 Hours |
| Revision & Notes | 30 Minutes |

---

# 📚 Recommended Documentation

- OpenAI Platform
- Anthropic Documentation
- Google Gemini Documentation
- LangChain Documentation
- LangGraph Documentation
- Model Context Protocol (MCP)
- FastAPI
- ChromaDB
- FAISS
- PGVector
- Docker

---

# ✅ Learning Outcomes

After completing this roadmap, you will be able to:

- Build AI chatbots and assistants
- Design effective prompts and structured outputs
- Implement function and tool calling
- Build Retrieval-Augmented Generation (RAG) systems
- Work with vector databases and embeddings
- Develop AI agents using LangChain and LangGraph
- Build and integrate MCP servers and clients
- Design multi-agent workflows
- Evaluate, monitor, and secure AI applications
- Deploy production-ready AI systems with FastAPI and Docker
- Architect scalable enterprise AI platforms