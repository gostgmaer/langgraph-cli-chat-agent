# AI Engineering Learning Roadmap

> Living roadmap. Update this document as new topics are completed.

## Overall Progress

**Completion:** \~60%

------------------------------------------------------------------------

# ✅ Completed

## Phase 1 --- Python Foundation

-   [x] Variables, Data Types, Functions
-   [x] Classes, Dataclasses, Enums
-   [x] Type Hints
-   [x] Async/Await
-   [x] Context Managers
-   [x] Decorators (Basics)
-   [x] Project Structure
-   [x] Dependency Injection
-   [x] Configuration
-   [x] Logging
-   [x] Exception Handling
-   [x] CLI Architecture

### Project

-   CLI AI Chatbot Foundation

------------------------------------------------------------------------

## Phase 2 --- LLM Architecture

-   [x] LLM Providers
-   [x] Provider Abstraction
-   [x] Model Registry
-   [x] Chat Models
-   [x] Streaming
-   [x] Token Usage
-   [x] Context Window
-   [x] Temperature / Top-P
-   [x] Multi-provider Design

### Providers

-   [x] Gemini
-   [x] OpenAI
-   [x] Anthropic
-   [x] Groq

### Project

-   Multi-provider LLM Manager

------------------------------------------------------------------------

## Phase 3 --- Session Architecture

-   [x] Session Lifecycle
-   [x] Thread IDs
-   [x] Conversation Management
-   [x] Session Storage
-   [x] Context Handling

### Project

-   Persistent CLI Sessions

------------------------------------------------------------------------

## Phase 4 --- LangGraph Fundamentals

-   [x] GraphState
-   [x] StateGraph
-   [x] Nodes
-   [x] Edges
-   [x] Conditional Routing
-   [x] Graph Compilation
-   [x] Execution
-   [x] Reducers
-   [x] add_messages()

### Project

-   Weather + Search Agent

------------------------------------------------------------------------

## Phase 5 --- ReAct Agents

-   [x] ReAct
-   [x] Tool Calling
-   [x] ToolNode
-   [x] bind_tools()
-   [x] tools_condition()
-   [x] AIMessage
-   [x] ToolMessage

### Project

-   Tool-enabled Assistant

------------------------------------------------------------------------

## Phase 6 --- Checkpoints

-   [x] Checkpointer
-   [x] Persistence
-   [x] Resume
-   [x] History
-   [x] Immutable Checkpoints

### Project

-   Durable Conversations

------------------------------------------------------------------------

## Phase 7 --- Streaming

-   [x] invoke()
-   [x] stream()
-   [x] astream()
-   [x] Token Streaming
-   [x] Runtime Timeline

### Project

-   Streaming Chat UI (CLI)

------------------------------------------------------------------------

## Phase 8 --- Runtime & Events

-   [x] Runtime Events
-   [x] Event Lifecycle
-   [x] Execution Tree
-   [x] Runnable Hierarchy
-   [x] run_id
-   [x] thread_id
-   [x] checkpoint_id

### Project

-   Runtime Event Inspector

------------------------------------------------------------------------

## Phase 9 --- Runnable Architecture

-   [x] Runnable API
-   [x] Pipelines
-   [x] Graph
-   [x] Prompt
-   [x] LLM
-   [x] Retriever
-   [x] Output Parser

### Project

-   Custom Runnable Library

------------------------------------------------------------------------

## Phase 10 --- Interrupts & HITL

-   [x] interrupt()
-   [x] Command()
-   [x] Resume
-   [x] Human Approval
-   [x] Long-running Workflows

### Project

-   Human Approval Workflow

------------------------------------------------------------------------

## Phase 11 --- Memory

-   [x] Short-term Memory
-   [x] Long-term Memory
-   [x] Semantic Memory
-   [x] Episodic Memory
-   [x] User Profile Memory
-   [x] Memory Extraction
-   [x] Memory Retrieval
-   [x] Memory Ranking
-   [x] Memory Lifecycle

### Project

-   AI Assistant with Long-term Memory

------------------------------------------------------------------------

## Phase 12 --- RAG (Completed Portion)

### Learned

-   [x] RAG vs Memory
-   [x] Embeddings
-   [x] Vector Dimensions
-   [x] Cosine Similarity
-   [x] Metadata
-   [x] Chunking
-   [x] Vector Databases
-   [x] Discovery
-   [x] Loaders
-   [x] Content Extraction
-   [x] Cleaning
-   [x] Batch Embedding
-   [x] Async Indexing
-   [x] Incremental Indexing
-   [x] Embedding Cache
-   [x] Validation
-   [x] Monitoring

### Project

-   Production Document Indexer

------------------------------------------------------------------------

# 🚧 Pending

## Phase 12 --- Retrieval Pipeline

-   [ ] Query Processing
-   [ ] Query Expansion
-   [ ] Query Embedding
-   [ ] Similarity Search
-   [ ] Top-K Retrieval
-   [ ] Metadata Filtering
-   [ ] Dense Retrieval
-   [ ] Sparse Retrieval
-   [ ] Hybrid Search
-   [ ] Re-ranking
-   [ ] MMR
-   [ ] Context Assembly
-   [ ] Prompt Construction
-   [ ] Citation Generation

### Project

Production RAG Chatbot

------------------------------------------------------------------------

## Phase 13 --- Advanced RAG

-   [ ] Parent-Child Retrieval
-   [ ] Multi-vector Retrieval
-   [ ] Recursive Retrieval
-   [ ] Graph RAG
-   [ ] Knowledge Graph
-   [ ] Multi-tenant RAG
-   [ ] Permission-aware Retrieval
-   [ ] Hallucination Detection
-   [ ] RAG Evaluation
-   [ ] RAGAS

### Project

Enterprise Knowledge Assistant

------------------------------------------------------------------------

## Phase 14 --- Advanced LangGraph

-   [ ] Subgraphs
-   [ ] Parallel Execution
-   [ ] Dynamic Routing
-   [ ] Retry Policies
-   [ ] Recovery
-   [ ] Fallback Nodes
-   [ ] Durable Execution

### Project

Workflow Automation Engine

------------------------------------------------------------------------

## Phase 15 --- LangChain Deep Dive

-   [ ] LCEL
-   [ ] Prompt Templates
-   [ ] Retrievers
-   [ ] Text Splitters
-   [ ] Document Transformers
-   [ ] Callbacks
-   [ ] Middleware
-   [ ] Custom Components

### Project

Custom LangChain Framework

------------------------------------------------------------------------

## Phase 16 --- Multi-Agent Systems

-   [ ] Supervisor Pattern
-   [ ] Planner Pattern
-   [ ] Worker Pattern
-   [ ] Swarm
-   [ ] Agent Delegation
-   [ ] Shared Memory
-   [ ] Coordination

### Project

Research Agent Team

------------------------------------------------------------------------

## Phase 17 --- MCP

-   [ ] MCP Architecture
-   [ ] MCP Client
-   [ ] MCP Server
-   [ ] Resources
-   [ ] Tools
-   [ ] Authentication
-   [ ] Production MCP

### Project

Custom MCP Server

------------------------------------------------------------------------

## Phase 18 --- Production AI Engineering

-   [ ] Background Jobs
-   [ ] Queue Systems
-   [ ] Redis
-   [ ] BullMQ
-   [ ] Kafka Basics
-   [ ] Distributed Workers
-   [ ] Idempotency
-   [ ] Rate Limiting
-   [ ] Circuit Breakers
-   [ ] LangSmith
-   [ ] OpenTelemetry
-   [ ] Monitoring
-   [ ] Cost Tracking

### Project

Production AI Platform

------------------------------------------------------------------------

## Phase 19 --- Deployment

-   [ ] Docker
-   [ ] Docker Compose
-   [ ] Kubernetes
-   [ ] CI/CD
-   [ ] Secrets
-   [ ] Auto Scaling
-   [ ] Production Deployment

### Project

Cloud-native AI Platform

------------------------------------------------------------------------

## Phase 20 --- Capstone

Build a production AI SaaS including: - \[ \] Multi-Agent - \[ \]
Production RAG - \[ \] Long-term Memory - \[ \] MCP - \[ \]
Multi-provider LLM - \[ \] Authentication - \[ \] Multi-tenancy - \[ \]
Observability - \[ \] Queue Processing - \[ \] Production Deployment

------------------------------------------------------------------------

## Final Outcome

By completing this roadmap you will be able to: - Design AI
architectures from scratch. - Build production-ready AI agents. -
Engineer scalable RAG systems. - Develop multi-agent platforms. - Deploy
enterprise AI applications. - Debug LangGraph/LangChain internals. -
Design reliable AI infrastructure.
