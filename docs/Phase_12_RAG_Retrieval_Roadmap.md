# Phase 12 --- Production RAG (Next Learning Module)

> Current Focus: **Retrieval Pipeline**

------------------------------------------------------------------------

# What We've Completed

## Foundations

-   ✅ RAG vs Memory
-   ✅ Embeddings
-   ✅ Vector Space
-   ✅ Cosine Similarity
-   ✅ Metadata
-   ✅ Chunking
-   ✅ Vector Databases

## Production Indexing

-   ✅ Discovery
-   ✅ Loader
-   ✅ Content Extraction
-   ✅ Cleaning
-   ✅ Metadata Pipeline
-   ✅ Batch Embedding
-   ✅ Async Indexing
-   ✅ Incremental Indexing
-   ✅ Embedding Cache
-   ✅ Validation
-   ✅ Monitoring

------------------------------------------------------------------------

# Retrieval Pipeline

``` text
User Question
      │
      ▼
Query Processing
      │
      ▼
Query Understanding
      │
      ▼
Query Expansion
      │
      ▼
Query Embedding
      │
      ▼
Metadata Filtering
      │
      ▼
Vector Search
      │
      ▼
Top-K Retrieval
      │
      ▼
Hybrid Search
      │
      ▼
Re-ranking
      │
      ▼
Context Compression
      │
      ▼
Prompt Construction
      │
      ▼
LLM
      │
      ▼
Final Answer
```

------------------------------------------------------------------------

# Module 1 --- Query Processing

## Topics

-   [ ] User Query
-   [ ] Query Normalization
-   [ ] Query Classification
-   [ ] Intent Detection
-   [ ] Query Rewriting
-   [ ] Query Expansion
-   [ ] Query Decomposition

### Mini Project

Build a query preprocessing pipeline that: - Cleans user input - Detects
intent - Rewrites ambiguous queries - Expands search keywords

------------------------------------------------------------------------

# Module 2 --- Query Embeddings

-   [ ] Query Embedding
-   [ ] Semantic Representation
-   [ ] Embedding Consistency
-   [ ] Cross-model Issues

### Mini Project

Visualize document and query embeddings using the same embedding model.

------------------------------------------------------------------------

# Module 3 --- Retrieval

-   [ ] Vector Search
-   [ ] ANN Search
-   [ ] Similarity Metrics
-   [ ] Top-K Retrieval
-   [ ] Score Threshold

### Mini Project

Implement a semantic retriever over a document collection.

------------------------------------------------------------------------

# Module 4 --- Metadata Filtering

-   [ ] Tenant Filtering
-   [ ] Permission Filtering
-   [ ] Namespace Filtering
-   [ ] Date Filters
-   [ ] Source Filters

### Mini Project

Build a multi-tenant retriever with metadata filters.

------------------------------------------------------------------------

# Module 5 --- Hybrid Search

-   [ ] Dense Retrieval
-   [ ] Sparse Retrieval
-   [ ] BM25
-   [ ] Hybrid Search
-   [ ] Reciprocal Rank Fusion (RRF)

### Mini Project

Compare BM25, Vector Search, and Hybrid Search on the same dataset.

------------------------------------------------------------------------

# Module 6 --- Re-ranking

-   [ ] Cross Encoder
-   [ ] Bi Encoder
-   [ ] MMR
-   [ ] Diversity Ranking
-   [ ] Duplicate Removal

### Mini Project

Improve retrieval quality using a re-ranking stage.

------------------------------------------------------------------------

# Module 7 --- Context Building

-   [ ] Context Window
-   [ ] Chunk Ordering
-   [ ] Context Compression
-   [ ] Parent Document Retrieval
-   [ ] Token Budgeting

### Mini Project

Implement dynamic context assembly before sending prompts to the LLM.

------------------------------------------------------------------------

# Module 8 --- Prompt Construction

-   [ ] Context Injection
-   [ ] Citation Formatting
-   [ ] Guardrails
-   [ ] System Prompt Design
-   [ ] Response Formatting

### Mini Project

Create a production-ready RAG prompt template.

------------------------------------------------------------------------

# Module 9 --- Response Evaluation

-   [ ] Hallucination Detection
-   [ ] Citation Verification
-   [ ] Faithfulness
-   [ ] Context Precision
-   [ ] Answer Quality

### Mini Project

Build an automated evaluation pipeline for RAG responses.

------------------------------------------------------------------------

# Next Major Phase

After completing the Retrieval Pipeline we will move to **Advanced
RAG**, including:

-   Parent-Child Retrieval
-   Multi-Vector Retrieval
-   Recursive Retrieval
-   Graph RAG
-   Knowledge Graph Integration
-   Agentic RAG
-   Multi-tenant RAG
-   Permission-aware Retrieval
-   RAG Evaluation (RAGAS)
-   Production Optimization
