# RAG System Architecture & Data Flow

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RAG NEWS SYSTEM ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   News Sources  │    │   Web Scraper   │    │   Text Chunker  │
│                 │───▶│                 │───▶│                 │
│ • Times of India│    │ • BeautifulSoup │    │ • 200 words     │
│ • Hindu         │    │ • Requests      │    │ • 50 overlap    │
│ • NDTV          │    │ • HTML Parser   │    │ • Metadata      │
│ • Indian Express│    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Vector Search  │    │ Embedding Model │    │   ChromaDB      │
│                 │◀───│                 │───▶│                 │
│ • Similarity    │    │ • MiniLM-L6-v2  │    │ • Vector Store  │
│ • Top-K Results │    │ • 384 dimensions│    │ • Metadata      │
│ • Relevance     │    │ • Semantic      │    │ • Persistence   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              ▲
         ▼                                              │
┌─────────────────┐    ┌─────────────────┐             │
│   User Query    │    │  Context Builder│─────────────┘
│                 │───▶│                 │
│ • Terminal Input│    │ • Chunk Combine │
│ • Question Text │    │ • Prompt Format │
│ • Natural Lang. │    │ • Source Track  │
└─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Final Answer   │    │   Gemini AI     │    │   RAG Pipeline  │
│                 │◀───│                 │◀───│                 │
│ • Generated Text│    │ • LLM Response  │    │ • Context + Q   │
│ • Source Links  │    │ • Natural Lang. │    │ • Prompt Eng.   │
│ • Confidence    │    │ • Contextual    │    │ • Error Handle  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Detailed Data Flow

### Phase 1: Data Ingestion & Processing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA INGESTION PIPELINE                          │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: Web Scraping
┌─────────────────┐
│ News Websites   │
│                 │
│ URL List:       │
│ ├─ TOI          │
│ ├─ Hindu        │
│ ├─ NDTV         │
│ ├─ Express      │
│ └─ HT           │
└─────────────────┘
         │ HTTP Requests
         ▼
┌─────────────────┐
│ HTML Content    │
│                 │
│ Raw Data:       │
│ ├─ <title>      │
│ ├─ <p> tags     │
│ ├─ <div> text   │
│ └─ Metadata     │
└─────────────────┘
         │ BeautifulSoup
         ▼
┌─────────────────┐
│ Clean Articles  │
│                 │
│ Structured:     │
│ ├─ Title        │
│ ├─ Content      │
│ ├─ URL          │
│ ├─ Source       │
│ └─ Timestamp    │
└─────────────────┘

Step 2: Text Processing
         │ Text Chunking
         ▼
┌─────────────────┐
│ Article Chunks  │
│                 │
│ Chunk 1:        │
│ ├─ 200 words    │
│ ├─ Metadata     │
│ └─ Chunk ID     │
│                 │
│ Chunk 2:        │
│ ├─ 150 new +    │
│ │  50 overlap   │
│ └─ Metadata     │
└─────────────────┘
         │ Sentence Transformer
         ▼
┌─────────────────┐
│ Vector Embeddings│
│                 │
│ Chunk 1:        │
│ [0.2, -0.1, 0.8,│
│  0.3, -0.5, ... │
│  ... 384 dims]  │
│                 │
│ Chunk 2:        │
│ [0.1, 0.4, -0.2,│
│  0.7, 0.1, ...  │
│  ... 384 dims]  │
└─────────────────┘
         │ Storage
         ▼
┌─────────────────┐
│ ChromaDB        │
│                 │
│ Collections:    │
│ ├─ Embeddings   │
│ ├─ Documents    │
│ ├─ Metadata     │
│ └─ IDs          │
└─────────────────┘
```

### Phase 2: Query Processing & Retrieval

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           QUERY PROCESSING PIPELINE                         │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: User Input
┌─────────────────┐
│ Terminal Input  │
│                 │
│ "What's the     │
│ latest news     │
│ about Indian    │
│ politics?"      │
└─────────────────┘
         │ Text Processing
         ▼
┌─────────────────┐
│ Query Embedding │
│                 │
│ Question Vector:│
│ [0.3, 0.1, -0.4,│
│  0.6, -0.2, ... │
│  ... 384 dims]  │
└─────────────────┘

Step 2: Vector Search
         │ Similarity Search
         ▼
┌─────────────────┐
│ ChromaDB Query  │
│                 │
│ Search Process: │
│ ├─ Cosine Sim   │
│ ├─ Top-K (5)    │
│ ├─ Threshold    │
│ └─ Ranking      │
└─────────────────┘
         │ Results
         ▼
┌─────────────────┐
│ Retrieved Chunks│
│                 │
│ Chunk A: 0.89   │
│ "Parliament     │
│ passed new..."  │
│                 │
│ Chunk B: 0.85   │
│ "Election       │
│ results show..."│
│                 │
│ Chunk C: 0.82   │
│ "PM announced..."│
└─────────────────┘

Step 3: Context Building
         │ Aggregation
         ▼
┌─────────────────┐
│ Context Window  │
│                 │
│ Combined Text:  │
│ "Parliament     │
│ passed new bill │
│ regarding...    │
│ Election results│
│ show significant│
│ changes... PM   │
│ announced new   │
│ policies..."    │
│                 │
│ Sources:        │
│ ├─ TOI/article1 │
│ ├─ Hindu/news2  │
│ └─ NDTV/story3  │
└─────────────────┘
```

### Phase 3: Answer Generation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ANSWER GENERATION PIPELINE                         │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: Prompt Engineering
┌─────────────────┐
│ Prompt Template │
│                 │
│ "You are a      │
│ helpful news    │
│ assistant.      │
│                 │
│ Context:        │
│ [Retrieved Text]│
│                 │
│ Question:       │
│ [User Query]    │
│                 │
│ Provide clear   │
│ organized answer│
│ with formatting"│
└─────────────────┘
         │ API Call
         ▼
┌─────────────────┐
│ Gemini AI       │
│                 │
│ Model:          │
│ gemini-1.5-flash│
│                 │
│ Processing:     │
│ ├─ Context      │
│ ├─ Question     │
│ ├─ Generation   │
│ └─ Formatting   │
└─────────────────┘
         │ Response
         ▼
┌─────────────────┐
│ Generated Answer│
│                 │
│ "Based on recent│
│ news, Indian    │
│ politics is     │
│ currently       │
│ focused on:     │
│                 │
│ 1. New bill     │
│    passage...   │
│ 2. Election     │
│    outcomes...  │
│ 3. Policy       │
│    changes..."  │
└─────────────────┘

Step 2: Response Formatting
         │ Terminal Display
         ▼
┌─────────────────┐
│ Final Output    │
│                 │
│ ═══════════════ │
│ ANSWER:         │
│ ═══════════════ │
│ [Generated Text]│
│                 │
│ ═══════════════ │
│ SOURCES (3):    │
│ ═══════════════ │
│ 1. TOI/article1 │
│ 2. Hindu/news2  │
│ 3. NDTV/story3  │
│                 │
│ 📊 Used 3 chunks│
└─────────────────┘
```

## Component Interactions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           COMPONENT INTERACTION MAP                          │
└─────────────────────────────────────────────────────────────────────────────┘

main.py
├─ Initializes RAGSystem()
├─ Calls load_news()
├─ Handles user input loop
└─ Formats output display

rag_system.py
├─ Coordinates all components
├─ Manages API connections
├─ Handles error cases
└─ Orchestrates RAG pipeline

scraper.py
├─ HTTP requests to news sites
├─ HTML parsing with BeautifulSoup
├─ Text extraction and cleaning
└─ Returns structured articles

embeddings.py
├─ Text chunking with overlap
├─ Embedding generation
├─ ChromaDB operations
└─ Vector similarity search

External Services:
├─ Google Gemini API
├─ News websites
└─ ChromaDB storage

Data Flow Direction:
News Sites → Scraper → Embeddings → ChromaDB → RAG → Gemini → User
```

## Performance Considerations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PERFORMANCE METRICS                              │
└─────────────────────────────────────────────────────────────────────────────┘

Bottlenecks:
├─ Web scraping: 2-5 seconds per site
├─ Embedding generation: 100ms per chunk
├─ Vector search: 50ms for similarity
└─ Gemini API: 1-3 seconds for response

Optimizations:
├─ Persistent ChromaDB storage
├─ Batch embedding processing
├─ Cached embeddings
└─ Efficient chunking strategy

Scalability:
├─ Can handle 1000+ articles
├─ Sub-second retrieval
├─ Parallel processing ready
└─ Incremental updates
```

This architecture ensures efficient news processing, accurate retrieval, and intelligent answer generation through the RAG pipeline.